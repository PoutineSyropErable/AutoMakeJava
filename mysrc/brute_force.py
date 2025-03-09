#!/home/francois/MainPython_Virtual_Environment/pip_venv/bin/python
import os
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Tuple

from graphviz import Digraph
import javalang


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


def generate_dependency_tree_brute_force(java_file_path: str, project_root_path: str):
    """Finds all dependencies recursively for a given Java file."""

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
    queue = [java_file_path]

    while queue:
        current_file = queue.pop(0)
        _, imports = get_imports_and_package(current_file)

        for imp in imports:
            if imp in java_files and java_files[imp] not in dependencies:
                dependencies.add(java_files[imp])
                queue.append(java_files[imp])

    return dependencies
