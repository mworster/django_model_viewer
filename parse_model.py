import ast
import os
from pathlib import Path

SELF_FILE = os.path.basename(__file__)

def get_py_files_in_dir():
    return [f for f in os.listdir('.') if f.endswith('.py') and f != SELF_FILE]

def resolve_imports(tree):
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == 'django.db.models':
                for alias in node.names:
                    aliases[alias.asname or alias.name] = f'django.db.models.{alias.name}'
            elif node.module == 'django.db':
                for alias in node.names:
                    if alias.name == 'models':
                        aliases[alias.asname or alias.name] = 'django.db.models'
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == 'django.db.models':
                    aliases[alias.asname or alias.name] = 'django.db.models'
    return aliases

def is_model_class(class_node, aliases):
    for base in class_node.bases:
        if isinstance(base, ast.Attribute):
            if isinstance(base.value, ast.Name):
                base_path = f"{aliases.get(base.value.id, base.value.id)}.{base.attr}"
                if base_path == 'django.db.models.Model':
                    return True
        elif isinstance(base, ast.Name):
            # handle direct "Model" if it's imported like "from django.db.models import Model"
            resolved = aliases.get(base.id, '')
            if resolved == 'django.db.models.Model':
                return True
    return False

def parse_model_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source, filename=file_path)
    aliases = resolve_imports(tree)
    models = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and is_model_class(node, aliases):
            fields = []
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    try:
                        field_type = stmt.value.func.attr if isinstance(stmt.value.func, ast.Attribute) else stmt.value.func.id
                        field_name = stmt.targets[0].id
                        fields.append((field_type, field_name))
                    except Exception:
                        pass
            models.append((node.name, fields))
    return models

def display_model(model_name, fields):
    max_width = max(len(f"{typ} {name}") for typ, name in fields) + 10
    border = '*' * max_width
    title = f"** model: {model_name} **"
    print(border)
    print(title.center(max_width))
    print(border)
    for typ, name in fields:
        line = f"*** {typ:<10} {name} ***"
        print(line.ljust(max_width, '*'))
    print(border + "\n")

def main():
    file_input = input("Enter Python file(s) to parse (comma-separated), or press Enter to auto-discover: ").strip()

    if file_input:
        files = [f.strip() for f in file_input.split(',')]
    else:
        files = get_py_files_in_dir()

    if not files:
        print("❌ No Python files found.")
        return

    for file in files:
        if not os.path.isfile(file):
            print(f"⚠️ Skipping {file} (not found)")
            continue

        print(f"🔍 Parsing {file}...")
        try:
            models = parse_model_file(file)
            if not models:
                print("❌ No valid Django models found in", file, "\n")
                continue

            for model_name, fields in models:
                display_model(model_name, fields)
        except Exception as e:
            print(f"⚠️ Error parsing {file}: {e}")

if __name__ == '__main__':
    main()
