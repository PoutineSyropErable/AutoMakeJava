import javalang
from javalang.tree import CompilationUnit
from typing import Tuple
from find_dependency_tree_helper import find_file_dependencies
import os


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


def get_imports(tree, module_to_path, path_to_module):
    """
    Extracts and resolves all imports in a Java file using module_to_path and path_to_module.

    Args:
        tree: Parsed Java AST.
        module_to_path (dict): Dictionary mapping module names to file paths.
        path_to_module (dict): Dictionary mapping file paths to module names.

    Returns:
        list: A list of resolved module names (fully qualified imports).
    """
    imports = []

    for imp in tree.imports:
        imported_module = imp.path  # Full import path as a string (e.g., "pack.Cat")

        if imp.wildcard:  # Handles `import pack.*;`
            if imported_module in module_to_path:  # Check if the package exists
                package_path = module_to_path[imported_module]
                if os.path.exists(package_path) and os.path.isdir(package_path):  # Ensure it's a directory
                    for file in os.listdir(package_path):
                        if file.endswith(".java"):
                            class_name = file.replace(".java", "")
                            full_module = f"{imported_module}.{class_name}"  # Convert to full module name
                            if full_module in module_to_path:
                                imports.append(full_module)
        else:  # Regular imports (`import pack.Cat;`)
            if imported_module in module_to_path:  # Only add if it exists
                imports.append(imported_module)

    return imports


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
