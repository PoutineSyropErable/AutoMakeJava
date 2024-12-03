import javalang


def parse_java_file(file_path):
    """Reads and parses a Java file, returning the AST."""
    with open(file_path, "r") as file:
        content = file.read()
    return javalang.parse.parse(content)


def get_imports(tree):
    """Extracts and returns all imports in the Java file."""
    return [imp.path for imp in tree.imports]


def get_class_methods(tree):
    """Returns a mapping of classes to their defined methods."""
    class_methods = {}
    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        methods = [
            method.name
            for method in node.methods
            if isinstance(method, javalang.tree.MethodDeclaration)
        ]
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


def analyze_java_file(file_path):
    """Analyzes a Java file and returns its imports, class-method mappings, and method calls."""
    tree = parse_java_file(file_path)
    imports = get_imports(tree)
    class_methods = get_class_methods(tree)
    method_calls = get_method_calls_with_context(tree)
    return imports, class_methods, method_calls


def find_file_dependencies(java_file_path, imports, method_calls):
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
            dependencies[caller] = (
                matching_imports if matching_imports else ["Unknown Source"]
            )

    return dependencies


if __name__ == "__main__":
    # Path to the main Java file
    java_file_path = "MainFile.java"

    # Analyze the Java file
    imports, class_methods, method_calls = analyze_java_file(java_file_path)

    # Find file dependencies
    file_dependencies = find_file_dependencies(java_file_path, imports, method_calls)

    # Print the results
    print(f"Imports: {imports}")
    print(f"Class Definitions and Methods: {class_methods}")
    print("Method Calls with Context:")
    for caller, method in method_calls:
        print(f"  - {method} called by {caller}")
    print("File Dependencies:")
    for caller, files in file_dependencies.items():
        print(f"  - {caller}: {', '.join(files)}")
