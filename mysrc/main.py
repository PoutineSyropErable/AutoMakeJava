import javalang

def get_includes(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    tree = javalang.parse.parse(content)
    imports = [imp.path for imp in tree.imports]
    return imports

