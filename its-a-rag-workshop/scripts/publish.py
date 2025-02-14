import json
import sys
import re

def clear_notebook_output(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)

def remove_solution_from_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'\s*## BEGIN SOLUTION ##.*?## END SOLUTION ##[\\n]*', '', content, flags=re.DOTALL)
    with open(notebook_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: publish.py <notebook_path>")
        sys.exit(1)
    file = sys.argv[1]
    clear_notebook_output(file)
    remove_solution_from_notebook(file)
