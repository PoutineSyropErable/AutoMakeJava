#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import os, sys
import javalang
from graphviz import Digraph


# List of files indicating the root of a Java project
PROJECT_ROOT_FILES = {".git", "pom.xml", "build.gradle", "build.xml", ".classpath", ".project"}


def find_base_directory(java_file, max_depth=10):
    """Backtrack up to 10 times or until '/' is reached, looking for a Java project root."""
    current_dir = os.path.abspath(os.path.dirname(java_file))  # Start from file's directory

    for _ in range(max_depth):
        # Check if any root marker exists in the current directory
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in PROJECT_ROOT_FILES):
            return current_dir  # Found root

        # Stop if we reach root `/` or `C:\` on Windows
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Reached root
            break

        current_dir = parent_dir  # Move up one level

    raise AssertionError("Couldn't find project root")


def parse_java_file(file_path):
    """Reads and parses a Java file, returning the AST and content."""
    with open(file_path, "r") as file:
        content = file.read()
    tree = javalang.parse.parse(content)
    return tree, content


def get_package(tree):
    """Extracts the package declaration from the AST."""
    if tree.package:
        return tree.package.name
    return None


def get_imports(tree):
    """Extracts and returns all imports in the Java file."""
    return [imp.path for imp in tree.imports]


def get_method_calls_with_context(tree):
    """Extracts method calls and their class or object context."""
    method_calls = []
    for _, node in tree.filter(javalang.tree.MethodInvocation):
        # Identify the calling class or object, if available
        caller = node.qualifier if node.qualifier else "unknown (local or implicit)"
        method_calls.append((caller, node.member))
    return method_calls


def find_file_dependencies(java_file_path, package, imports, method_calls, base_dir):
    """
    Determines file dependencies for a given Java file based on method calls,
    imports, and the package declaration.

    Args:
        java_file_path (str): Path to the Java file.
        package (str): Package name of the Java file.
        imports (list): List of imported packages or classes in the file.
        method_calls (list): List of tuples with (caller, method) for method calls.
        base_dir (str): Base directory to resolve file paths.

    Returns:
        dict: A mapping of called classes to the imported packages or files they map to.
    """
    dependencies = {}

    for caller, method in method_calls:
        if caller != "unknown (local or implicit)":
            # Match the caller to imports or same-package classes
            matching_imports = [imp for imp in imports if caller in imp.split(".")]
            if matching_imports:
                # Map the class to the matching import
                dependencies[caller] = matching_imports[0]
            else:
                # Check if the caller is in the same package
                if package:
                    potential_path = os.path.join(
                        base_dir,
                        package.replace(".", os.sep),
                        f"{caller}.java",
                    )
                    if os.path.exists(potential_path):
                        dependencies[caller] = potential_path
                    else:
                        dependencies[caller] = "Unknown Source"
    return dependencies


def generate_dependency_tree(java_file_path, base_dir, tree=None, visited=None) -> dict:
    """
    Recursively generates a dependency tree for a given Java file.

    Args:
        java_file_path (str): Path to the root Java file.
        base_dir (str): Base directory to resolve file paths.
        tree (dict): Current dependency tree being constructed.
        visited (set): Set of visited files to prevent infinite recursion.

    Returns:
        dict: A hierarchical dependency tree.
    """
    if tree is None:
        tree = {}
    if visited is None:
        visited = set()

    # Skip if the file is already visited
    if java_file_path in visited:
        return tree
    visited.add(java_file_path)

    # Parse the Java file
    try:
        tree_ast, content = parse_java_file(java_file_path)
    except Exception as e:
        print(f"Error parsing {java_file_path}: {e}")
        return tree

    # Extract package, imports, and method calls
    package = get_package(tree_ast)
    imports = get_imports(tree_ast)
    method_calls = get_method_calls_with_context(tree_ast)

    # Find dependencies
    dependencies = find_file_dependencies(java_file_path, package, imports, method_calls, base_dir)

    # Add to the tree
    tree[java_file_path] = {}

    for _, dependency in dependencies.items():
        # Resolve file path for the dependency
        if dependency != "Unknown Source":
            if not dependency.endswith(".java"):
                dependency_path = os.path.join(base_dir, dependency.replace(".", os.sep) + ".java")
            else:
                dependency_path = dependency

            if os.path.exists(dependency_path):
                tree[java_file_path][dependency_path] = {}
                generate_dependency_tree(dependency_path, base_dir, tree[java_file_path], visited)

    return tree


def visualize_dependency_tree(tree, output_path="dependency_tree"):
    """
    Visualizes the dependency tree using Graphviz.

    Args:
        tree (dict): Dependency tree to visualize.
        output_path (str): Output file path for the visualization.
    """
    dot = Digraph(comment="Java Dependency Tree")

    def add_edges(node, parent=None):
        for child, subtree in node.items():
            if parent:
                dot.edge(parent, child)
            add_edges(subtree, child)

    add_edges(tree)
    dot.render(output_path, format="png", cleanup=True)
    print(f"Dependency tree visualization saved as {output_path}.png")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python script.py <path-to-java-file>")
        sys.exit(1)

    print("\n\n-----------------Start of Program ---------------\n\n")
    java_file = sys.argv[1]
    base_directory = find_base_directory(java_file)
    print(f"Java file = {java_file},\nproject root = {base_directory}\n\n")

    # Generate the dependency tree
    dependency_tree: dict = generate_dependency_tree(java_file, base_directory)

    # Print the tree structure for debugging
    print(f"Dependency Tree: (Length: {len(dependency_tree)})")
    print(dependency_tree)

    if len(dependency_tree) < 2:
        print("\ndependency_tree is empty\n")
        exit(0)

    print("\n\n\n")
    # Visualize the dependency tree
    visualize_dependency_tree(dependency_tree)
