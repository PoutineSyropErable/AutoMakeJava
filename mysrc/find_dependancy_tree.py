#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import sys
from find_dependancy_tree_helper import *


def test_helper(java_file_path, project_root_path):
    tree_ast, content = parse_java_file(java_file_path)
    package = get_package(tree_ast)
    imports = get_imports(tree_ast)
    method_calls = get_method_calls_with_context(tree_ast)
    print(f"package = {package}")
    print(f"imports = {imports}")
    print(f"method_calls = {method_calls}")


def main(java_file_path: str, project_root_path: str):
    print(f"Java file = {java_file_path},")
    print(f"project root = {project_root_path}\n\n")

    resolved_deps = generate_dependency_tree_brute_force(java_file_path, project_root_path)

    if resolved_deps:
        print("\nResolved Dependencies:")
        for dep in resolved_deps:
            print(dep)

    print("\n\n\n")
    test_helper(java_file_path, project_root_path)
    dependency_tree: dict = generate_dependency_tree(java_file_path, project_root_path)

    # Print the tree structure for debugging
    print("\n\n")
    print(f"Dependency Tree: (Length: {len(dependency_tree)})")
    print(dependency_tree)

    if len(dependency_tree) < 2:
        print("\ndependency_tree is empty\n")
        exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_dependancy_tree.py <path-to-java-file>")
        sys.exit(1)

    print("\n\n-----------------Start of Program ---------------\n\n")
    java_file_path = sys.argv[1]
    project_root_path = find_base_directory(java_file_path)

    main(java_file_path, project_root_path)
