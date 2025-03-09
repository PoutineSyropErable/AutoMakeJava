import javalang
from javalang.tree import CompilationUnit
from typing import Tuple
from find_dependency_tree_helper import find_file_dependencies


def parse_java_file(file_path) -> Tuple[CompilationUnit, str]:
    """Reads and parses a Java file, returning the AST and content."""
    with open(file_path, "r") as file:
        content: str = file.read()
    tree: CompilationUnit = javalang.parse.parse(content)
    return tree, content


def get_package(tree):
    """Extracts the package declaration from the AST."""
    if tree.package:
        return tree.package.name
    return None


import os


import os


def get_imports(tree, project_root_path, source_dirs):
    """
    Extracts and returns all imports in the Java file, resolving wildcard imports (e.g., `import pack.*;`).

    Args:
        tree: Parsed Java AST.
        project_root_path (str): Root directory of the project.
        source_dirs (list): List of possible source directories.

    Returns:
        list: A list of imported classes/packages, resolving `import pack.*;`.
    """
    imports = []

    for imp in tree.imports:
        import_found = False  # Track if we found the import

        if imp.wildcard:  # Handles `import pack.*;`
            for src_dir in source_dirs:
                package_path = os.path.join(project_root_path, src_dir, imp.path.replace(".", os.sep))

                if os.path.exists(package_path) and os.path.isdir(package_path):
                    for file in os.listdir(package_path):
                        if file.endswith(".java"):
                            class_name = file.replace(".java", "")
                            imports.append(f"{imp.path}.{class_name}")  # Store full class path
                    import_found = True
                    break  # Stop searching once found in a source directory

        else:  # Regular imports (`import pack.Cat;`)
            for src_dir in source_dirs:
                import_path = os.path.join(project_root_path, src_dir, imp.path.replace(".", os.sep) + ".java")

                if os.path.exists(import_path):
                    imports.append(imp.path)  # Found a valid import
                    import_found = True
                    break  # Stop searching once found

        # If an import wasn't found in any source directory, keep it as is
        if not import_found:
            imports.append(imp.path)

    return imports


def get_class_methods(tree):
    """Returns a mapping of classes to their defined methods."""
    class_methods = {}
    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        methods = [method.name for method in node.methods if isinstance(method, javalang.tree.MethodDeclaration)]
        class_methods[node.name] = methods
    return class_methods


def get_method_calls_with_context(tree):
    """Extracts method calls and their class or object context."""
    method_calls = []
    for _, node in tree.filter(javalang.tree.MethodInvocation):
        # Identify the calling class or object, if available
        caller = node.qualifier if node.qualifier else "unknown (local or implicit)"
        method_calls.append((caller, node.member))
    return method_calls


def get_instantiations(tree_ast):
    """
    Extracts instantiated class names from a Java AST.
    """
    instantiated_classes = set()

    for path, node in tree_ast:
        if isinstance(node, javalang.tree.ClassCreator):  # Matches `new ClassName(...)`
            class_name = node.type.name
            instantiated_classes.add(class_name)

    return instantiated_classes


def analyze_java_file(java_file_path):
    raise NotImplementedError("analyze java file not implemented")
    tree_ast, content = parse_java_file(java_file_path)
    package = get_package(tree_ast)
    imports = get_imports(tree_ast, ".")
    method_calls = get_method_calls_with_context(tree_ast)
    instantiations = get_instantiations(tree_ast)
    return package, imports, method_calls, instantiations


def find_file_dependencies_basic(java_file_path, imports, method_calls):
    """
    Determines file dependencies for a given Java file based on method calls
    and imports.

    Args:
        java_file_path (str): Path to the Java file.
        imports (list): List of imported packages or classes in the file.
        method_calls (list): List of tuples with (caller, method) for method calls.

    Returns:
        dict: A mapping of called classes to the imported packages or files they map to.
    """
    # Mapping dependencies
    dependencies = {}

    # For each method call, try to map it to an imported file or class
    for caller, method in method_calls:
        if caller != "unknown (local or implicit)":
            # Find the corresponding import
            matching_imports = [imp for imp in imports if caller in imp.split(".")]
            dependencies[caller] = matching_imports if matching_imports else ["Unknown Source"]

    return dependencies


if __name__ == "__main__":
    # Path to the main Java file
    java_file_path = "MainFile.java"

    # Analyze the Java file
    imports, class_methods, method_calls, instantiations = analyze_java_file(java_file_path)

    # Find file dependencies
    exit(0)
    file_dependencies = find_file_dependencies(java_file_path, imports, method_calls, ".")

    # Print the results
    print(f"Imports: {imports}")
    print(f"Class Definitions and Methods: {class_methods}")
    print("Method Calls with Context:")
    for caller, method in method_calls:
        print(f"  - ({method}) called by ({caller})")
    print("File Dependencies:")
    for caller, files in file_dependencies.items():
        print(f"  - ({caller}): ({', '.join(files)})")
