#!/home/francois/PythonVenv/pip_venv/bin/python
import os, sys
import subprocess
import xml.etree.ElementTree as ET


from find_dependency_tree_helper import find_base_directory
from find_dependency_tree import main as get_compilation_order

from config import CAPTURE_OUTPUT, send_notification, PRINT_OUTPUT, DEBUG_, DEBUG_PORT, COMPILE_ONLY, SOCKET_LISTEN
from config import parse_classpath


def compile_project(project_root_path, compilation_order, output_dir, classpath, module_to_path, debug=False):
    """
    Compiles all Java files in the correct dependency order.

    Args:
        project_root_path (str): Root directory of the project.
        compilation_order (list[list[str]]): Ordered list of Java modules to compile.
        output_dir (str): Directory where compiled .class files will be stored.
        classpath (str): The full classpath string for dependencies.
    """
    for java_group in compilation_order:
        java_files = [module_to_path[module] for module in java_group]  # Get file paths
        if PRINT_OUTPUT:
            print(f"Compiling: {java_files}")

        compile_cmd = [
            "javac",
            "-d",
            output_dir,  # Set output directory for .class files
            "-cp",
            f"{output_dir}:{classpath}",  # Classpath includes compiled files + dependencies
        ]

        if debug:
            compile_cmd.append("-g")  # Enable debugging information

        compile_cmd.extend(java_files)  # Append Java files to compile

        result = subprocess.run(compile_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            if PRINT_OUTPUT:
                print("❌ Compilation failed!")
                print(result.stderr)
            return False  # Stop execution if compilation fails

    if PRINT_OUTPUT:
        print("✅ Compilation successful!")
    return True  # Indicate successful compilation


def execute_java_file(java_file_path, output_dir, classpath, path_to_module, debug=False):
    """
    Executes the compiled Java file.

    Args:
        java_file_path (str): Path to the main Java file to execute.
        output_dir (str): Directory containing compiled .class files.
        classpath (str): The full classpath string for execution.
    """
    main_class = path_to_module[java_file_path]  # Convert Java file path to module name
    if PRINT_OUTPUT:
        print(f"Executing: {main_class}")

    run_cmd = [
        "java",
        "-cp",
        f"{output_dir}:{classpath}",  # Classpath includes compiled files + dependencies
    ]
    if debug:
        if SOCKET_LISTEN:
            run_cmd.append(f"-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:{DEBUG_PORT}")
        if PRINT_OUTPUT:
            print(f"🔍 Debug mode enabled: Listening for debugger on port {DEBUG_PORT}...")

    run_cmd.append(main_class)  # Append main class name

    if not CAPTURE_OUTPUT:
        if PRINT_OUTPUT:
            print("🎉 Program output:\n")
            print("------------------------ Start of Java Program ------------------------------")
        print("", flush=True)

        subprocess.run(run_cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        return

    # if Capture Output
    result = subprocess.run(run_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        if PRINT_OUTPUT:
            print("❌ Execution failed!")
            print(result.stderr)
    else:
        if PRINT_OUTPUT:
            print("🎉 Program output:\n")
            print("------------------------ Start of Java Program ------------------------------")
            print(result.stdout)

    return


def extract_classpath_from_xml(classpath_file, project_root: str):
    """
    Parses Eclipse .classpath XML and returns:
    - The absolute path of the output directory.
    - A Java-compatible classpath string.

    Args:
        classpath_file (str): Path to the .classpath XML file.

    Returns:
        tuple: (absolute_output_dir, classpath_string)
    """
    project_root = os.path.dirname(classpath_file)  # Get the project root directory
    tree = ET.parse(classpath_file)
    root = tree.getroot()

    classpath_entries = []
    output_dir = None

    for entry in root.findall("classpathentry"):
        kind = entry.get("kind")
        path = entry.get("path")
        if not isinstance(path, str) and not path:
            raise AssertionError("path inexistant")

        if kind == "src":
            classpath_entries.append(os.path.join(project_root, path))  # Absolute source directories
        elif kind == "output":
            output_dir = os.path.join(project_root, path)  # Ensure absolute path for output directory
        elif kind == "lib":
            classpath_entries.append(path)  # External JARs (already absolute)

    if output_dir is None:
        raise ValueError("No output directory found in .classpath file")

    return output_dir, ":".join(classpath_entries)  # Return absolute output directory & classpath


def main(java_file_path, project_root_path, debug=False):
    if DEBUG_:
        print("\n\n-----------------Start of Program ---------------\n\n")

    compilation_order, module_to_path, path_to_module = get_compilation_order(java_file_path, project_root_path)
    classpath_file = f"{project_root_path}/.classpath"
    if DEBUG_:
        print(f"classpath_file = {classpath_file}")
    output_dir, classpath = extract_classpath_from_xml(classpath_file, project_root_path)
    output_dir = os.path.realpath(output_dir)

    if DEBUG_:
        print(f"output_dir = {output_dir}\n")
        print(f"classpath = {classpath}")

    result = parse_classpath(classpath_file, project_root_path)
    if result["suggested_moves"]:
        print("\n💡 Suggested Moves:")
        for old_path, new_path in result["suggested_moves"]:
            print(f"🔄 Move: {old_path} → {new_path}")
        print("\nRun the following command to move JUnit files:")
        for old_path, new_path in result["suggested_moves"]:
            print(f"mv {old_path} {new_path}")

    # Compile project
    if compile_project(project_root_path, compilation_order, output_dir, classpath, module_to_path, debug=debug):
        if not COMPILE_ONLY:
            # Execute only if compilation succeeds
            if PRINT_OUTPUT:
                print("")
            execute_java_file(java_file_path, output_dir, classpath, path_to_module, debug=debug)

    return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_dependency_tree.py <path-to-java-file>")
        sys.exit(1)

    java_file_path = os.path.realpath(sys.argv[1])
    project_root_path = find_base_directory(java_file_path)
    # Check if --DEBUG_ is passed
    debug = "--debug" in sys.argv
    send_notification(f"debug={debug}", java_file_path)

    main(java_file_path, project_root_path, debug=debug)
