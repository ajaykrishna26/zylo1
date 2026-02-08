from pathlib import Path
p=Path('BACKEND/static/uploads')
if not p.exists():
    print('no uploads dir')
else:
    files=list(p.iterdir())
    if not files:
        print('no files')
    for f in files:
        print(f.name)
