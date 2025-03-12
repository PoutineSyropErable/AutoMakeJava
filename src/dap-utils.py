#!/home/francois/PythonVenv/pip_venv/bin/python
import os, sys
import argparse
import xml.etree.ElementTree as ET

from find_dependency_tree_helper import find_base_directory, get_source_dirs_from_classpath
from find_dependency_tree import main as get_compilation_order

from automake import execute_java_file, extract_classpath_from_xml, compile_project
from automake import main as automake_function


def get_mainfile_module_name(java_file_path: str, project_root_path: str, classpath_file: str, source_dirs: list[str] = ["src"]) -> int:

    java_file_path = os.path.realpath(java_file_path)  # Normalize the file path

    for src_dir in source_dirs:
        src_path = os.path.realpath(os.path.join(project_root_path, src_dir))  # Normalize source path

        if java_file_path.startswith(src_path):  # Ensure the file is within the source directory
            relative_path = os.path.relpath(java_file_path, src_path)  # Get path relative to src_dir
            module_name = relative_path.replace(os.sep, ".").replace(".java", "")  # Convert to dot notation
            print(f"{module_name}")
            return 0

    return 1
    raise ValueError(f"Error: The file '{java_file_path}' is not inside any recognized source directory.")


def get_class_path(java_file_path: str, project_root_path: str, classpath_file: str, source_dirs: list[str] = ["src"]) -> int:
    try:
        output_dir, classpath = extract_classpath_from_xml(classpath_file, project_root_path, debug=False)
    except:
        return 1

    print(f"{classpath}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select only one option from the available choices.")

    # Add a positional argument for the Java file
    parser.add_argument("java_file", help="Path to the Java file")
    # Creating a mutually exclusive group to ensure only one option is chosen
    group = parser.add_mutually_exclusive_group(required=True)

    # Boolean options (only one can be chosen at a time)
    group.add_argument("--mainModule", action="store_true", help="Get the name of the mainModule")
    group.add_argument("--getClassPath", action="store_true", help="Get the Java classpath")

    # Parse arguments
    args = parser.parse_args()

    # Dictionary switch statement mapping options to functions
    switch = {
        "mainModule": get_mainfile_module_name,
        "getClassPath": get_class_path,
    }

    # Ensure a Java file path is provided
    if len(sys.argv) < 2:
        print("Error: You must provide a Java file path as an argument.")
        sys.exit(1)

    java_file_path = os.path.realpath(args.java_file)
    project_root_path = find_base_directory(java_file_path)
    classpath_file = f"{project_root_path}/.classpath"
    source_dirs = get_source_dirs_from_classpath(classpath_file)

    # Find the active option and execute its function
    for key, func in switch.items():
        if getattr(args, key):  # Check which argument is True
            ret = func(java_file_path, project_root_path, classpath_file, source_dirs)
            break  # Exit once a function is called

    exit(ret)
