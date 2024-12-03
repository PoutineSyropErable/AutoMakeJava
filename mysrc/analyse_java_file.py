import javalang

def analyze_java_file(file_path):
    # Read the Java file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Parse the file with javalang
    tree = javalang.parse.parse(content)

    # Extract imports
    imports = [imp.path for imp in tree.imports]

    # Extract class-to-method mappings
    class_methods = {}
    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        methods = [
            method.name
            for method in node.methods
            if isinstance(method, javalang.tree.MethodDeclaration)
        ]
        class_methods[node.name] = methods

    # Extract method calls
    called_methods = [
        node.member for _, node in tree.filter(javalang.tree.MethodInvocation)
    ]

    return class_methods, called_methods, imports

if __name__ == "__main__":
    # Path to the main Java file
    java_file_path = "MainFile.java"

    # Analyze the Java file
    class_methods, called, imports = analyze_java_file(java_file_path)

    # Print the results
    print(f"Class Definitions and Methods: {class_methods}")
    print(f"Called Methods: {called}")
    print(f"Imports: {imports}")

