#!/home/francois/PythonVenv/pip_venv/bin/python
import os
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Tuple

# from graphviz import Digraph

from automake import DEBUG_

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
        raise AssertionError("\n\nSource dirs are empty, there's no source dir in classpath. Assuming src\n\n")
    return source_dirs


def build_project_module_maps(project_root_path, source_dirs):
    """
    Scans the project source directories and builds:
    1. A dictionary mapping Java file paths to module names.
    2. A dictionary mapping package directories to package names.
    3. Ensures module names do not contain `src.` or `mysrc.` prefixes.
    4. Uses real paths to avoid relative path issues.

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
        src_path = os.path.realpath(os.path.join(project_root_path, src_dir))  # Use realpath for consistency

        if not os.path.exists(src_path):
            continue  # Skip non-existent source directories

        for root, _, files in os.walk(src_path):
            root = os.path.realpath(root)  # Normalize root path

            # Compute package name relative to the src_dir
            relative_dir_path = os.path.relpath(root, src_path)
            package_name = relative_dir_path.replace(os.sep, ".") if relative_dir_path != "." else ""

            # Ensure no duplicate package exists in different source directories
            if package_name and package_name in package_dirs and package_dirs[package_name] != root:
                raise ValueError(
                    f"Error: Package '{package_name}' exists in multiple source directories: " f"{package_dirs[package_name]} and {root}"
                )

            # Store package directory (only if it's a package, not the root)
            if package_name:
                package_dirs[package_name] = root
                path_to_module[root] = package_name  # Directory to package name
                module_to_path[package_name] = root  # Package name to directory

            for file in files:
                if not file.endswith(".java"):  # Skip non-Java files
                    continue

                file_path = os.path.realpath(os.path.join(root, file))  # Use realpath

                # Convert file path to module name (without src. or mysrc. prefix)
                relative_path = os.path.relpath(file_path, src_path)
                module_name = relative_path.replace(os.sep, ".").replace(".java", "")  # Convert path to dot notation

                # If the file is directly inside `src/` or `mysrc/`, use only the filename
                if package_name == "":
                    module_name = file.replace(".java", "")

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


def get_all_java_files_depth_one(dir: str) -> list[str]:
    """Returns a list of Java files only in the given directory (depth = 1)."""
    return [os.path.join(dir, file) for file in os.listdir(dir) if file.endswith(".java") and os.path.isfile(os.path.join(dir, file))]


def find_file_dependencies_simple(package, imports, path_to_module: dict[str, str], module_to_path: dict[str, str]):
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
    dependencies = []
    if package != None:
        if DEBUG_:
            print(f"package = {package}")
            print(f"path = {module_to_path.get(package, 'failed')}")
        package_path = module_to_path[package]
        java_file_paths = get_all_java_files_depth_one(package_path)
        modules_in_package = []
        for java_file_path in java_file_paths:
            modules_in_package.append(path_to_module[java_file_path])

        dependencies += modules_in_package

    return dependencies + imports
