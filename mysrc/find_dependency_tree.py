#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import sys
import numpy as np
from find_dependency_tree_helper import *
from java_file_analyser import *
from brute_force import *


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
    print("\n")
    print(f"Inside module_to_path: direct_dependencies = {direct_dependencies}")
    # print(f"direct_dependencies = {direct_dependencies}")
    dependency_modules_paths = [dep.replace(".", "/") for dep in direct_dependencies]
    # print(f"dependency_modules_paths = {dependency_modules_paths}")

    possible_paths: list[list[str]] = [
        [project_root_path + "/" + src_dir + "/" + dep + ".java" for dep in dependency_modules_paths] for src_dir in source_dirs
    ]
    # print(f"possible_paths = {possible_paths}")
    output_dict = {}

    print("\n")
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
            print(f"\n\ndependency : {dep} didn't have a file found")

    return output_dict


def generate_dependency_tree(java_file_path, project_root_path, modules_to_path_dict: dict = {}) -> dict:
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
    dependency_tree_modules = {}

    classpath = f"{project_root_path}/.classpath"
    source_dirs = get_source_dirs_from_classpath(classpath)
    module_name_of_this = path_to_module(project_root_path, source_dirs, [java_file_path])[0]
    modules_to_path_dict[module_name_of_this] = java_file_path

    print(f"project root = {project_root_path}")
    print(f"source_dirs = {source_dirs}")
    print(f"Java file = {java_file_path},")
    print(f"Name of this module = {module_name_of_this}")

    # start of loop
    package, imports, method_calls = analyze_java_file(java_file_path)

    print("\n")
    print(f"package = {package}")
    print(f"imports = {imports}")
    print(f"method_calls = {method_calls}")

    module_dependency_dict = find_file_dependencies(java_file_path, package, imports, method_calls, project_root_path)
    # print(f"\nmodule Dependencies: \n{module_dependency_dict}")
    module_dependency = list(module_dependency_dict.values())

    direct_dependencies_path_dict = module_to_path(project_root_path, source_dirs, module_dependency, modules_to_path_dict)
    print(f"Dictionary of the module to path for the dependency of this file = \n{direct_dependencies_path_dict}\n")
    direct_dependencies_path = list(direct_dependencies_path_dict.values())
    print(f"Path to the direct dependency of this file= \n{direct_dependencies_path}\n")

    # end of loop
    print(f"\n\nDictionary: Module -> Path    =\n{modules_to_path_dict}\n")
    dependency_tree_modules[module_name_of_this] = list(direct_dependencies_path_dict.keys())
    print(f"Dependancy tree: {dependency_tree_modules}")

    return dependency_tree_modules


def main(java_file_path: str, project_root_path: str):

    module_to_path_dict = {}
    dependency_tree = generate_dependency_tree(java_file_path, project_root_path, module_to_path_dict)
    # Print the tree structure for debugging
    print("\n\n")
    print(f"Dependency Tree: (Length: {len(dependency_tree)})")
    print(dependency_tree)

    if len(dependency_tree) < 2:
        print("\ndependency_tree is empty\n")
        exit(0)

    resolved_deps = generate_dependency_tree_brute_force(java_file_path, project_root_path)

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
