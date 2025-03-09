import xml.etree.ElementTree as ET


def extract_classpath(classpath_file, output_file="classpath.txt"):
    """
    Extracts classpath entries from Eclipse .classpath file and saves them to classpath.txt.

    Args:
        classpath_file (str): Path to .classpath file.
        output_file (str): Output file name for simplified classpath.
    """
    tree = ET.parse(classpath_file)
    root = tree.getroot()

    classpath_entries = []

    for entry in root.findall("classpathentry"):
        kind = entry.get("kind")
        path = entry.get("path")

        if kind == "src":
            classpath_entries.append(f"./{path}")  # Source folders (relative paths)
        elif kind == "output":
            classpath_entries.append(f"./{path}")  # Output directory
        elif kind == "lib":
            classpath_entries.append(path)  # External libraries (absolute paths)

    # Join paths with ":" (Linux/macOS) or ";" (Windows)
    classpath_str = ":".join(classpath_entries)

    with open(output_file, "w") as f:
        f.write(classpath_str)

    print(f"\u2705 Extracted classpath saved to {output_file}")


# Example Usage
extract_classpath("./.classpath")
