import subprocess, sys

def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

print('Running git fetch origin...')
rc, out, err = run('git fetch origin')
if rc != 0:
    print('git fetch failed:', err)
    sys.exit(1)

rc, branch, err = run('git rev-parse --abbrev-ref HEAD')
if rc != 0:
    print('failed to get current branch:', err)
    sys.exit(1)
print('Current branch:', branch)

rc, divergence, err = run('git rev-list --left-right --count HEAD...origin/main')
if rc == 0:
    print('Divergence (ours...theirs):', divergence)
else:
    print('Could not compute divergence:', err)

rc, files, err = run('git diff --name-only HEAD...origin/main')
print('\nFiles differing between HEAD and origin/main:')
if files:
    print(files)
else:
    print('(no file-level differences)')

rc, base, err = run('git merge-base HEAD origin/main')
if rc != 0:
    print('git merge-base failed:', err)
    sys.exit(1)
print('\nMerge base commit:', base)

# run merge-tree to see if there are textual conflicts
rc, mt_out, mt_err = run(f'git merge-tree {base} HEAD origin/main')
print('\n--- git merge-tree output (truncated) ---')
if mt_out:
    lines = mt_out.splitlines()
    truncated = '\n'.join(lines[:400])
    print(truncated)
else:
    print('(no output)')

# quick check for conflict markers
conflict_markers = []
for marker in ['<<<<<<<', '=======', '>>>>>>>', 'CONFLICT']:
    if marker in mt_out:
        conflict_markers.append(marker)

print('\nConflict markers found in merge-tree output:', conflict_markers)

# Also list changed files with conflict potential via merge-tree diff heuristic
print('\nHeuristic: if the same file appears modified in both sides, conflict possible.')
rc, left_files, err = run('git diff --name-only $(git merge-base HEAD origin/main) HEAD')
rc2, right_files, err2 = run('git diff --name-only $(git merge-base HEAD origin/main) origin/main')
left_set = set(left_files.splitlines()) if left_files else set()
right_set = set(right_files.splitlines()) if right_files else set()
both = sorted(left_set & right_set)
print('Files modified on our branch since base:', len(left_set))
print('Files modified on origin/main since base:', len(right_set))
if both:
    print('Files modified in both (potential conflicts):')
    print('\n'.join(both))
else:
    print('No files modified in both since merge base.')

print('\nDone.')
