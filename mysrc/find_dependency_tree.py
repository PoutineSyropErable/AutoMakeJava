#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import os
import sys
import numpy as np
from find_dependency_tree_helper import *
from java_file_analyser import *
from brute_force import *

from collections import deque


def path_to_module(project_root_path: str, source_dirs: list[str], file_paths: list[str]) -> list[str]:
    absolute_paths = list(map(os.path.abspath, file_paths))
    module_names = []

    for file_path in absolute_paths:
        if not file_path.startswith(project_root_path):
            raise ValueError(f"File path {file_path} is outside the project root {project_root_path}")

        # Get the relative path inside the project
        relative_path = os.path.relpath(file_path, project_root_path)

        # Remove the first source directory from the path
        for src in source_dirs:
            if relative_path.startswith(f"{src}/") or relative_path == src:
                relative_path = relative_path[len(src) + 1 :]  # Remove "src/" or "mysrc/"
                break  # Only remove the first matching source directory

        # Remove `.java` extension and convert to Java module format
        if relative_path.endswith(".java"):
            relative_path = relative_path[:-5]  # Remove `.java` (5 chars)

        module_name = relative_path.replace("/", ".")  # Convert path separators to dots
        module_names.append(module_name)

    return module_names


def module_to_path(project_root_path: str, source_dirs: list[str], direct_dependencies: list[str], pre_calc: dict = {}) -> dict[str, str]:
    # print("\n")
    # print(f"Inside module_to_path: direct_dependencies = {direct_dependencies}")
    # print(f"direct_dependencies = {direct_dependencies}")
    dependency_modules_paths = [dep.replace(".", "/") for dep in direct_dependencies]
    # print(f"dependency_modules_paths = {dependency_modules_paths}")

    possible_paths: list[list[str]] = [
        [project_root_path + "/" + src_dir + "/" + dep + ".java" for dep in dependency_modules_paths] for src_dir in source_dirs
    ]
    # print(f"possible_paths = {possible_paths}")
    output_dict = {}

    # print("\n")
    for j, dep in enumerate(direct_dependencies):
        if dep in pre_calc:
            output_dict[dep] = pre_calc[dep]
            continue
        for i, src_dir in enumerate(source_dirs):
            possible_dep_path = possible_paths[i][j]
            # print(f"possible_dep_path = {possible_dep_path}")
            if os.path.exists(possible_dep_path):
                # print(f"{dep} is found at {possible_dep_path}")
                if dep in output_dict:
                    print(f"\n\nAlready found file for {dep} at {output_dict[dep]}\n")
                    raise KeyError("if it's at two location, idk what to do. Abborting.")

                output_dict[dep] = possible_dep_path
                pre_calc[dep] = possible_dep_path

    # print(f"\n\ndirect_dependencies_path = {output_dict}")
    for dep in direct_dependencies:
        if dep not in output_dict:
            print(f"dependency : {dep} didn't have a file found")

    return output_dict


def generate_dependency_tree(
    java_file_path: str,
    project_root_path: str,
    module_to_path: dict[str, str],
    path_to_module: dict[str, str],
    source_dirs: list[str] = ["src"],
) -> dict[str, list[str]]:
    """
    Generates a dependency tree for a given Java file using iterative tree traversal (BFS).

    Args:
        java_file_path (str): Path to the root Java file.
        project_root_path (str): Root directory of the Java project.
        modules_to_path_dict (dict, optional): Caching dictionary for module-to-path mapping.

    Returns:
        dict: A hierarchical dependency tree.
    """

    dependency_tree_modules = {}

    # Initialize queue for BFS traversal
    queue = deque()

    # Get module name for the root Java file
    module_name = path_to_module[java_file_path]
    module_to_path[module_name] = java_file_path
    queue.append(module_name)

    visited = set()

    while queue:
        print("\n")
        current_module = queue.popleft()  # Get the next module in BFS order
        if current_module in visited:
            continue

        visited.add(current_module)
        current_path = module_to_path[current_module]

        print(f"Processing module: {current_module} ({current_path})")

        # Analyze the file

        tree_ast, content = parse_java_file(java_file_path)
        imports = get_imports(tree_ast, project_root_path, source_dirs)
        package = get_package(tree_ast)

        print(f"package = {package}")
        print(f"imports = {imports}")
        # Not using method calls or instantiations
        # package, imports, method_calls, instantiations = analyze_java_file(current_path)

        # Determine dependencies
        module_dependency_dict = find_file_dependencies_simple(package, imports, path_to_module, module_to_path)
        print(f"module_dependency_dict = {module_dependency_dict}")
        module_dependency_names = list(module_dependency_dict.values())

        # Resolve paths of dependencies
        dependency_tree_modules[current_module] = list(direct_dependencies_path_dict.keys())
        print(f"Direct dependency_tree_modules = {dependency_tree_modules[current_module]}")

        # Add new dependencies to the queue
        for dep_module, dep_path in direct_dependencies_path_dict.items():
            if dep_module not in visited:
                module_to_path[dep_module] = dep_path
                queue.append(dep_module)

    return dependency_tree_modules


def main(java_file_path: str, project_root_path: str):

    module_to_path_dict = {}
    classpath = f"{project_root_path}/.classpath"
    source_dirs = get_source_dirs_from_classpath(classpath)
    path_to_module, module_to_path = build_project_module_maps(project_root_path, source_dirs)

    print(f"path_to_module =\n{path_to_module}\n")
    print(f"module_to_path =\n{module_to_path}\n")

    for java_file in path_to_module.values():
        print(java_file)

    print("\n\n")
    for java_file in path_to_module.keys():
        print(java_file)

    dependency_tree = generate_dependency_tree(java_file_path, project_root_path, module_to_path, path_to_module, source_dirs)

    # Print the tree structure for debugging
    print(f"Dependency Tree: (Length: {len(dependency_tree)})")
    print(dependency_tree)

    exit(0)
    # resolved_deps = generate_dependency_tree_brute_force(java_file_path, project_root_path)

    if resolved_deps:
        print("\nResolved Dependencies:")
        for dep in resolved_deps:
            print(dep)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_dependency_tree.py <path-to-java-file>")
        sys.exit(1)

    print("\n\n-----------------Start of Program ---------------\n\n")
    java_file_path = os.path.realpath(sys.argv[1])
    project_root_path = find_base_directory(java_file_path)

    main(java_file_path, project_root_path)
