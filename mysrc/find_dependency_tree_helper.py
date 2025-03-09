#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import os
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Tuple

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


def get_source_dirs_from_classpath(classpath_file) -> list[str]:
    """Parses .classpath to extract source directories."""
    tree = ET.parse(classpath_file)
    root = tree.getroot()
    source_dirs: list[str] = [str(entry.get("path")) for entry in root.findall(".//classpathentry[@kind='src']")]
    if len(source_dirs) == 0:
        print("\n\nSource dirs are empty, there's no source dir in classpath. Assuming src\n\n")
        return ["src"]
    return source_dirs


def build_project_module_maps(project_root_path, source_dirs):
    """
    Scans the project source directories and builds:
    1. A dictionary mapping Java file paths to module names.
    2. A dictionary mapping package directories to package names.
    3. Ensures module names do not contain `src.` or `mysrc.` prefixes.

    Args:
        project_root_path (str): Root directory of the project.
        source_dirs (list[str]): List of source directories to scan.

    Returns:
        tuple: (dict[path -> module], dict[module -> path])

    Raises:
        ValueError: If two different source directories contain the same package name.
    """
    path_to_module = {}  # Maps Java file paths & package directories to module/package names
    module_to_path = {}  # Maps module/package names to Java file paths & package directories
    package_dirs = {}  # Track package directories to detect duplicates

    for src_dir in source_dirs:
        src_path = os.path.join(project_root_path, src_dir)

        if not os.path.exists(src_path):
            continue  # Skip non-existent source directories

        for root, _, files in os.walk(src_path):
            # Convert root to package name
            relative_dir_path = os.path.relpath(root, src_path)  # Use src_path to remove src. or mysrc.
            if relative_dir_path == ".":
                continue  # Skip root directory itself

            package_name = relative_dir_path.replace(os.sep, ".")  # Convert path separators to dots

            # Ensure no duplicate package exists in different source directories
            if package_name in package_dirs and package_dirs[package_name] != root:
                raise ValueError(
                    f"Error: Package '{package_name}' exists in multiple source directories: " f"{package_dirs[package_name]} and {root}"
                )

            # Store package directory
            package_dirs[package_name] = root
            path_to_module[root] = package_name  # Directory to package name
            module_to_path[package_name] = root  # Package name to directory

            for file in files:
                if not file.endswith(".java"):  # Skip non-Java files
                    continue

                file_path = os.path.join(root, file)

                # Convert file path to module name (without src. or mysrc. prefix)
                relative_path = os.path.relpath(file_path, src_path)
                module_name = relative_path.replace(os.sep, ".").replace(".java", "")  # Convert path to dot notation

                # Populate dictionaries
                path_to_module[file_path] = module_name

                # Check for duplicate module definitions
                if module_name in module_to_path:
                    raise ValueError(
                        f"Error: Module '{module_name}' is defined in multiple locations: " f"{module_to_path[module_name]} and {file_path}"
                    )

                module_to_path[module_name] = file_path

    return path_to_module, module_to_path


def find_file_dependencies(java_file_path, package, imports, method_calls, base_dir=".") -> dict:
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
        # print(f"caller: {caller}, method: {method}")
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


def find_file_dependencies_simple(package, imports, path_to_module, module_to_path):
    """
    Determines file dependencies for a given Java file by:
    1. Treating all classes in the same package as internal dependencies.
    2. Mapping imports to external dependencies.
    3. Resolving internal project dependencies.

    Args:
        java_file_path (str): Path to the Java file.
        package (str): The package of the Java file.
        imports (list): List of imported classes/packages.
        project_root_path (str): Root directory of the project.

    Returns:
        dict: Mapping of dependencies (class/module names to file paths or import references).
    """
    dependencies = {}

    # Step 1: All classes in the same package are internal dependencies
    package_dir = os.path.join(project_root_path, package.replace(".", os.sep)) if package else project_root_path
    if os.path.exists(package_dir):
        for file in os.listdir(package_dir):
            if file.endswith(".java") and file != os.path.basename(java_file_path):
                class_name = file.replace(".java", "")
                dependencies[class_name] = os.path.join(package_dir, file)

    # Step 2: Map imports to possible locations in the project
    for imp in imports:
        imp_path = os.path.join(project_root_path, imp.replace(".", os.sep) + ".java")
        if os.path.exists(imp_path):
            dependencies[imp.split(".")[-1]] = imp_path  # Store only class name as key

    return dependencies


def generate_dependency_tree_complicated(java_file_path, project_root_path, modules_to_path_dict=None) -> dict:
    """
    Generates a dependency tree for a given Java file using iterative tree traversal (BFS).

    Args:
        java_file_path (str): Path to the root Java file.
        project_root_path (str): Root directory of the Java project.
        modules_to_path_dict (dict, optional): Caching dictionary for module-to-path mapping.

    Returns:
        dict: A hierarchical dependency tree.
    """
    if modules_to_path_dict is None:
        modules_to_path_dict = {}

    dependency_tree_modules = {}
    classpath = f"{project_root_path}/.classpath"
    source_dirs = get_source_dirs_from_classpath(classpath)

    # Initialize queue for BFS traversal
    queue = deque()

    # Get module name for the root Java file
    module_name = path_to_module(project_root_path, source_dirs, [java_file_path])[0]
    modules_to_path_dict[module_name] = java_file_path
    queue.append(module_name)

    visited = set()

    while queue:
        print("\n")
        current_module = queue.popleft()  # Get the next module in BFS order
        if current_module in visited:
            continue

        visited.add(current_module)
        current_path = modules_to_path_dict[current_module]

        print(f"Processing module: {current_module} ({current_path})")

        # Analyze the file
        package, imports, method_calls, instantiations = analyze_java_file(current_path)
        print(f"package = {package}")
        print(f"imports = {imports}")
        print(f"method_calls = {method_calls}")
        print(f"instantiations= {instantiations}")

        # Determine dependencies
        module_dependency_dict = find_file_dependencies_simple(package, imports, project_root_path, source_dirs)
        print(f"module_dependency_dict = {module_dependency_dict}")
        module_dependency_names = list(module_dependency_dict.values())

        # Resolve paths of dependencies
        direct_dependencies_path_dict = module_to_path(project_root_path, source_dirs, module_dependency_names, modules_to_path_dict)
        dependency_tree_modules[current_module] = list(direct_dependencies_path_dict.keys())
        print(f"Direct dependency_tree_modules = {dependency_tree_modules[current_module]}")

        # Add new dependencies to the queue
        for dep_module, dep_path in direct_dependencies_path_dict.items():
            if dep_module not in visited:
                modules_to_path_dict[dep_module] = dep_path
                queue.append(dep_module)

    return dependency_tree_modules


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
