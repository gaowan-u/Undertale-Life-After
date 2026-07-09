import glob, sys

targets = set()
import pythonforandroid.build as m
targets.add(m.__file__)
for p in glob.glob(
    '/home/user/.buildozer/android/platform/**/pythonforandroid/build.py',
    recursive=True,
):
    targets.add(p)

for path in sorted(targets):
    print('Checking', path)
    with open(path) as f:
        src = f.read()
    if 'pip install -U pip' not in src:
        print('  no upgrade line, skipping')
        continue
    src = src.replace('pip install -U pip', 'true')
    with open(path, 'w') as f:
        f.write(src)
    print('  patched')
