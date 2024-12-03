import javalang

def analyze_java_file(file_path):
    # Read the Java file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Parse the file with javalang
    tree = javalang.parse.parse(content)

    # Extract method definitions
    defined_methods = [
        method.name for _, method in tree.filter(javalang.tree.MethodDeclaration)
    ]

    # Extract method calls
    called_methods = [
        node.member for _, node in tree.filter(javalang.tree.MethodInvocation)
    ]

    return defined_methods, called_methods

if __name__ == "__main__":
    # Path to the test Java file
    java_file_path = "TestFile.java"

    # Analyze the Java file
    defined, called = analyze_java_file(java_file_path)

    # Print the results
    print(f"Defined Methods: {defined}")
    print(f"Called Methods: {called}")

