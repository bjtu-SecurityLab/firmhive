import os
import glob

def find_firmware_root(start_path, required_dirs=None, file_patterns=None, min_score=10):
    dir_weights = {
        'bin': 4, 'sbin': 3, 'lib': 4, 'etc': 3, 'usr': 2,
        'var': 1, 'www': 2, 'home': 1, 'dev': 1, 'mnt': 1, 'root': 2
    }
    file_weights = {
        'bin/busybox': 5, 'bin/sh': 5, 
        'etc/passwd': 3, 'etc/shadow': 3, 'etc/init.d': 2,
        'init': 4
    }
    required_dirs = required_dirs or dir_weights
    file_patterns = file_patterns or file_weights
    
    best = {'path': None, 'score': -999, 'depth': 999}

    def is_standard_fs(root):
        key_dirs = ['bin', 'etc', 'lib', 'sbin', 'usr', 'www']
        present_dirs = [d for d in key_dirs if os.path.isdir(os.path.join(root, d))]
        return len(present_dirs) >= 3

    norm_start_path = os.path.normpath(start_path)
    for root, dirs, _ in os.walk(norm_start_path):
        dirs[:] = [d for d in dirs if d not in {'.git', 'docs', 'examples', 'test', 'tests', 'samples'}]
        if any(x in root.lower().split(os.sep) for x in {'modules', 'kernel', 'drivers', 'scripts', 'build', 'doc'}):
            continue

        dir_score = sum(weight for d, weight in required_dirs.items() if os.path.isdir(os.path.join(root, d)))
        
        file_score = 0
        if dir_score > 5:
            file_score = sum(weight for pattern, weight in file_patterns.items() 
                             if glob.glob(os.path.join(root, pattern)))
        
        total_score = dir_score + file_score
        
        if is_standard_fs(root):
            total_score += 20
        
        basename = os.path.basename(root).lower()
        if 'root' in basename:
            total_score += 5
        if any(term in basename for term in {'squashfs', 'cramfs', 'jffs2', 'yaffs', 'rootfs', 'fs_root'}):
            total_score += 10

        if root == norm_start_path:
            depth = 0
        else:
            depth = len(os.path.relpath(root, norm_start_path).split(os.sep))
        total_score -= depth * 0.5

        if total_score > best['score'] or \
           (total_score == best['score'] and depth < best['depth']):
            best.update({'path': root, 'score': total_score, 'depth': depth})

    if best['score'] >= min_score:
        return os.path.normpath(best['path']) if best['path'] else None
    
    return None