from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parent.parent
for script in ['src/create-curriculum.py','scripts/check-catalog.py','scripts/assemble.py']:
    subprocess.run([sys.executable,'-X','utf8',str(root/script)],cwd=root,check=True)
print('Website built in docs/.')
