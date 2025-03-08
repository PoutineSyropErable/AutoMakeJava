#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import os
import re
import sys

# Common Java project indicators
PROJECT_ROOT_FILES = {".git", "pom.xml", "build.gradle", "build.xml", ".classpath", ".project"}


def find_base_directory(java_file, max_depth=10):
    """Finds the project root by backtracking up to 10 levels."""
    current_dir = os.path.abspath(os.path.dirname(java_file))

    for _ in range(max_depth):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in PROJECT_ROOT_FILES):
            return current_dir  # Found project root

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Stop at root `/`
            break
        current_dir = parent_dir

    return None  # No root found


def get_imports_and_package(java_file):
    """Extracts import statements and the package name from a Java file."""
    imports = set()
    package_name = None

    with open(java_file, "r") as f:
        for line in f:
            line = line.strip()
            # Extract package declaration
            if line.startswith("package "):
                package_name = line.split(" ")[1].rstrip(";")  # Extracts `utils` from `package utils;`
            # Extract import statements
            elif line.startswith("import "):
                match = re.match(r"import\s+([\w\.]+);", line)
                if match:
                    imports.add(match.group(1))  # Example: utils.Helper

    return package_name, imports


def resolve_dependencies(main_java_file):
    """Finds all dependencies recursively for a given Java file."""

    print(f"Project Root Found: {project_root_path}")

    # Build a map of all Java files in the project
    java_files = {}
    for root, _, files in os.walk(project_root_path):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                package, _ = get_imports_and_package(file_path)

                if package:
                    class_name = f"{package}.{file.replace('.java', '')}"  # Example: utils.Helper
                else:
                    class_name = file.replace(".java", "")  # No package case

                java_files[class_name] = file_path  # Store full path

    # Resolve dependencies recursively
    dependencies = set()
    queue = [main_java_file]

    while queue:
        current_file = queue.pop(0)
        _, imports = get_imports_and_package(current_file)

        for imp in imports:
            if imp in java_files and java_files[imp] not in dependencies:
                dependencies.add(java_files[imp])
                queue.append(java_files[imp])

    return dependencies


def main(java_file_path: str, project_root_path: str):
    print(f"Java file = {java_file_path},")
    print(f"project root = {project_root_path}\n\n")

    resolved_deps = resolve_dependencies(java_file_path)

    if resolved_deps:
        print("\nResolved Dependencies:")
        for dep in resolved_deps:
            print(dep)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_dependancy_tree.py <path-to-java-file>")
        sys.exit(1)

    print("\n\n-----------------Start of Program ---------------\n\n")
    java_file_path = sys.argv[1]

    project_root_path = find_base_directory(java_file_path)
    if not project_root_path:
        print("\n\n")
        raise AssertionError("Java project root not found")

    main(java_file_path, project_root_path)
