#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import os
import sys
import numpy as np
from find_dependency_tree_helper import *
from java_file_analyser import *
from brute_force import *

from collections import defaultdict, deque


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
    debug: bool = False,
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
        if debug:
            print("\n")
        current_module = queue.popleft()  # Get the next module in BFS order
        if current_module in visited:
            continue

        visited.add(current_module)
        current_path = module_to_path[current_module]

        if debug:
            print(f"Processing module: {current_module} ({current_path})")

        # Analyze the file

        tree_ast, content = parse_java_file(current_path)
        imports = get_imports(tree_ast, module_to_path, path_to_module)
        package = get_package(tree_ast)

        if debug:
            print(f"package = {package}, {type(package)}")
            print(f"imports = {imports}")
        # Not using method calls or instantiations
        # package, imports, method_calls, instantiations = analyze_java_file(current_path)

        # Determine dependencies
        module_dependency_names = find_file_dependencies_simple(package, imports, path_to_module, module_to_path)

        if debug:
            print(f"module_dependency_names = {module_dependency_names}")
        dependency_tree_modules[current_module] = module_dependency_names

        # Add new dependencies to the queue
        for dep_module in module_dependency_names:
            if dep_module not in visited:
                queue.append(dep_module)

    return dependency_tree_modules


def purge_self_dependencies(dependency_tree):
    """
    Removes self-dependencies from the dependency tree.

    Args:
        dependency_tree (dict): A dictionary where keys are module names,
                                and values are lists of dependencies.

    Returns:
        dict: A cleaned dependency tree without self-references.
    """
    cleaned_tree = {}
    for module, dependencies in dependency_tree.items():
        cleaned_tree[module] = [dep for dep in dependencies if dep != module]
    return cleaned_tree


from collections import deque


from collections import defaultdict, deque


def find_cycles(dependency_tree):
    """
    Detects cycles in the dependency tree using Tarjan's Strongly Connected Components (SCC) algorithm.

    Args:
        dependency_tree (dict): A dictionary mapping modules to their dependencies.

    Returns:
        list of lists: Each inner list is a group of files that must be compiled together.
    """
    index = 0
    stack = []
    indices = {}
    lowlinks = {}
    on_stack = set()
    sccs = []

    def strongconnect(node):
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in dependency_tree.get(node, []):
            if neighbor not in indices:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])

        if lowlinks[node] == indices[node]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            sccs.append(scc)

    for node in dependency_tree:
        if node not in indices:
            strongconnect(node)

    return sccs


def get_compilation_batches(dependency_tree):
    """
    Computes a valid compilation order considering cyclic dependencies.

    - Groups files in cycles together into a single compilation batch.
    - Sorts independent files using topological sorting.

    Args:
        dependency_tree (dict): A dictionary where keys are module names,
                                and values are lists of dependencies.

    Returns:
        list: A list of compilation steps (each step is a list of files to compile together).
    """
    # Step 1: Detect strongly connected components (cycles)
    sccs = find_cycles(dependency_tree)

    # Create a mapping of modules to their SCC group
    module_to_scc = {}
    for scc in sccs:
        for module in scc:
            module_to_scc[module] = tuple(scc)  # Use a tuple for immutability

    # Step 2: Build a new DAG (dependency graph) of SCCs
    scc_graph = defaultdict(set)
    scc_in_degree = {scc: 0 for scc in map(tuple, sccs)}

    for module, dependencies in dependency_tree.items():
        for dep in dependencies:
            if module_to_scc[module] != module_to_scc[dep]:  # Ignore internal cycle dependencies
                scc_graph[module_to_scc[module]].add(module_to_scc[dep])

    # Step 3: Compute topological ordering of SCCs
    scc_in_degree = {scc: 0 for scc in map(tuple, sccs)}
    for deps in scc_graph.values():
        for dep in deps:
            scc_in_degree[dep] += 1

    # Start with SCCs that have no incoming dependencies
    queue = deque([scc for scc in scc_in_degree if scc_in_degree[scc] == 0])
    compilation_batches = []

    while queue:
        scc = queue.popleft()
        compilation_batches.append(list(scc))  # Each SCC is compiled together

        for neighbor in scc_graph[scc]:
            scc_in_degree[neighbor] -= 1
            if scc_in_degree[neighbor] == 0:
                queue.append(neighbor)

    return compilation_batches[::-1]


def main(java_file_path: str, project_root_path: str, debug: bool = False):

    module_to_path_dict = {}
    classpath = f"{project_root_path}/.classpath"
    source_dirs = get_source_dirs_from_classpath(classpath)
    path_to_module, module_to_path = build_project_module_maps(project_root_path, source_dirs)

    if debug:
        print(f"path_to_module =\n{path_to_module}\n")
        print(f"module_to_path =\n{module_to_path}\n")

    for java_file in path_to_module.values():
        if debug:
            print(java_file)

    if debug:
        print("\n\n")
    for java_file in path_to_module.keys():
        if debug:
            print(java_file)

    if debug:
        print("\n\n")

    dependency_tree = generate_dependency_tree(java_file_path, project_root_path, module_to_path, path_to_module, source_dirs)
    dependency_tree = purge_self_dependencies(dependency_tree)

    # Print the tree structure for debugging
    if debug:
        print(f"Dependency Tree: (Length: {len(dependency_tree)})")
        print(dependency_tree)

    compilation_order = get_compilation_batches(dependency_tree)
    if debug:
        print("\n")
        print(f"compilation_order = {compilation_order}")

    return compilation_order, module_to_path, path_to_module


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_dependency_tree.py <path-to-java-file>")
        sys.exit(1)

    print("\n\n-----------------Start of Program ---------------\n\n")
    java_file_path = os.path.realpath(sys.argv[1])
    project_root_path = find_base_directory(java_file_path)

    main(java_file_path, project_root_path)
