import os
from pathlib import Path

def verify_project_structure():
    required_files = [
        'manage.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        'LICENSE',
        'CONTRIBUTING.md',
        'pm_quest/__init__.py',
        'pm_quest/settings.py',
        'pm_quest/urls.py',
        'pm_quest/wsgi.py',
        'game/__init__.py',
        'game/admin.py',
        'game/apps.py',
        'game/models.py',
        'game/tests.py',
        'game/views.py',
        'static/css/style.css',
        'static/js/game.js'
    ]
    
    required_dirs = [
        'pm_quest',
        'game',
        'game/templates',
        'game/templates/game',
        'game/fixtures',
        'static',
        'static/css',
        'static/js',
        'static/images'
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Check files
    for file_path in required_files:
        if not os.path.isfile(file_path):
            missing_files.append(file_path)
    
    # Check directories
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            missing_dirs.append(dir_path)
    
    return missing_files, missing_dirs

def main():
    missing_files, missing_dirs = verify_project_structure()
    
    if not missing_files and not missing_dirs:
        print("✅ Project structure is complete!")
        return
    
    if missing_files:
        print("\n❌ Missing files:")
        for file in missing_files:
            print(f"  - {file}")
    
    if missing_dirs:
        print("\n❌ Missing directories:")
        for directory in missing_dirs:
            print(f"  - {directory}")
        
    print("\nPlease create the missing files and directories to complete the project structure.")

if __name__ == "__main__":
    main()