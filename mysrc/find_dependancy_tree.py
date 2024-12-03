import os
import javalang
from graphviz import Digraph


def parse_java_file(file_path):
    """Reads and parses a Java file, returning the AST."""
    with open(file_path, 'r') as file:
        content = file.read()
    return javalang.parse.parse(content)


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


def find_file_dependencies(java_file_path, imports, method_calls, base_dir):
    """
    Determines file dependencies for a given Java file based on method calls
    and imports.

    Args:
        java_file_path (str): Path to the Java file.
        imports (list): List of imported packages or classes in the file.
        method_calls (list): List of tuples with (caller, method) for method calls.
        base_dir (str): Base directory to resolve file paths.

    Returns:
        dict: A mapping of called classes to the imported packages or files they map to.
    """
    dependencies = {}

    for caller, method in method_calls:
        if caller != "unknown (local or implicit)":
            matching_imports = [
                imp for imp in imports if caller in imp.split(".")
            ]
            if matching_imports:
                # Map the class to the matching import file
                dependencies[caller] = matching_imports[0]
            else:
                dependencies[caller] = "Unknown Source"

    return dependencies


def generate_dependency_tree(java_file_path, base_dir, tree=None, visited=None):
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
        tree_ast = parse_java_file(java_file_path)
    except Exception as e:
        print(f"Error parsing {java_file_path}: {e}")
        return tree

    # Extract imports and method calls
    imports = get_imports(tree_ast)
    method_calls = get_method_calls_with_context(tree_ast)

    # Find dependencies
    dependencies = find_file_dependencies(java_file_path, imports, method_calls, base_dir)

    # Add to the tree
    tree[java_file_path] = {}

    for _, dependency in dependencies.items():
        # Resolve file path for the dependency
        dependency_path = os.path.join(base_dir, dependency.replace(".", os.sep) + ".java")
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
    import sys

    if len(sys.argv) != 3:
        print("Usage: python dependency_tree.py <path_to_java_file> <base_directory>")
        sys.exit(1)

    java_file = sys.argv[1]
    base_directory = sys.argv[2]

    # Generate the dependency tree
    dependency_tree = generate_dependency_tree(java_file, base_directory)

    # Visualize the dependency tree
    visualize_dependency_tree(dependency_tree)

    # Print the tree structure for debugging
    print("Dependency Tree:")
    print(dependency_tree)

