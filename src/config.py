import subprocess
import os
import xml.etree.ElementTree as ET


CAPTURE_OUTPUT = False  # keep it to false for real time commands
PRINT_OUTPUT = False  # For the main print output
DEBUG_ = False  # Show debug statement for this one (More ingrained then print output)

DEBUG_PORT = 5005
LOCAL_JUNIT_PATH = os.path.expanduser("~/.local/java/junit/")


def send_notification(title: str, message: str, timeSeconds: float = 5):
    """
    Sends a desktop notification using notify-send (Linux).

    Args:
        title (str): Title of the notification.
        message (str): Body text of the notification.
    """
    try:
        subprocess.run(["notify-send", "-t", str(int(timeSeconds * 1000)), title, message], check=True)
    except FileNotFoundError:
        print("❌ notify-send is not installed or not available in PATH.")
    except subprocess.CalledProcessError:
        print("❌ Failed to send notification.")


def get_system_java_home():
    """
    Returns the system's Java home path by checking `java.home`.
    """
    try:
        java_home_output = subprocess.run(
            ["java", "-XshowSettings:properties", "-version"],
            stderr=subprocess.PIPE,
            text=True,
        ).stderr
        for line in java_home_output.splitlines():
            if "java.home" in line:
                return line.split("=")[-1].strip()
    except Exception as e:
        print(f"❌ Error checking system Java: {e}")
    return None


def parse_classpath(classpath_file, project_root_path):
    """
    Parses an Eclipse .classpath file, replaces `JRE_CONTAINER`, and checks if paths exist.

    Args:
        classpath_file (str): Path to the .classpath XML file.
        project_root_path (str): Root directory of the project.

    Returns:
        dict: A dictionary containing existing and missing paths.
    """
    if not os.path.exists(classpath_file):
        print(f"❌ Error: Classpath file '{classpath_file}' not found.")
        raise FileNotFoundError(f"File not found: {classpath_file}")

    tree = ET.parse(classpath_file)
    root = tree.getroot()

    java_home = get_system_java_home()
    if not java_home:
        print("⚠️ Warning: Could not determine Java home. JRE_CONTAINER paths may be incorrect.")

    paths = []
    missing_paths = []
    suggested_moves = []

    for entry in root.findall("classpathentry"):
        path = entry.get("path")
        if not path:
            continue  # Skip if there's no path attribute

        # Replace JRE_CONTAINER with the detected Java home
        if "JRE_CONTAINER" in path and java_home:
            full_path = java_home
        elif not path.startswith("/"):  # Handle relative paths
            full_path = os.path.join(project_root_path, path)
        else:
            full_path = path  # Absolute path

        # Check if the file or directory exists
        if os.path.exists(full_path):
            paths.append(full_path)
            print(f"✅ Exists: {full_path}")
        else:
            missing_paths.append(full_path)
            print(f"❌ Missing: {full_path}")

            # Suggest moving JUnit libraries to ~/.local
            if "/usr/lib/jvm/junit" in full_path:
                local_path = os.path.join(LOCAL_JUNIT_PATH, os.path.basename(full_path))
                suggested_moves.append((full_path, local_path))

    return {
        "existing": paths,
        "missing": missing_paths,
        "suggested_moves": suggested_moves,
    }
