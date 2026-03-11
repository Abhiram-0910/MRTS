import os

def rename_mirai():
    dirs_to_check = ['.', 'backend', 'frontend']
    target = 'Movie and TV Shows Recommending Engine'
    replacement = 'Movie and TV Shows Recommending Engine'
    
    for d in dirs_to_check:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            if 'frontend-react' in root or 'venv' in root or '.git' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if not file.endswith(('.py', '.md', '.bat', '.sh', '.yaml', '.yml', '.txt', '.json')):
                    continue
                    
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if target in content:
                        new_content = content.replace(target, replacement)
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated {path}")
                except Exception as e:
                    print(f"Failed {path}: {e}")

if __name__ == "__main__":
    rename_mirai()
