import os
import shutil
import subprocess
from pathlib import Path

def setup_glowing_enigma():
    """Setup the glowing-enigma repository and its dependencies"""
    base_dir = Path(__file__).parent
    repo_dir = base_dir / 'glowing-enigma'
    
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    
    subprocess.run([
        'git', 'clone',
        'https://github.com/kafitimi/glowing-enigma.git',
        str(repo_dir)
    ], check=True)
    
    subprocess.run([
        'pip', 'install', '-r',
        str(repo_dir / 'requirements.txt')
    ], check=True)

if __name__ == '__main__':
    setup_glowing_enigma()