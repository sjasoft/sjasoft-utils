import os
from contextlib import contextmanager

@contextmanager
def directory(path):
    '''
    Used with 'with' block executes within the given directory and then returns to original directory.
    Basically a pushd/popd wrapper.
    :param path: path to execute within.
    :return:
    '''
    current = os.path.abspath('.')
    target = os.path.abspath(path)
    changed = target != current
    if changed:
        os.chdir(path)
    yield
    if changed:
        os.chdir(current)


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def walkup(start):
    param = start[:-1] if start.endswith('/') else start
    if not param:
        return None
    return os.path.dirname(param)

def walk_up_find(to_find, start='.'):
    start = os.path.abspath(start)
    if not os.path.isdir(start):
        start = os.path.dirname(start)
    while start and not os.path.exists(os.path.join(start, to_find)):
        start = walkup(start)
    return os.path.join(start, to_find) if start else None

def up_dir(n, path):
    res = path
    for _ in range(n):
        res = os.path.dirname(res)
    return res

def walk_doing_files(start, file_filter, file_action, return_files=False):
    good, bad = [], {}
    for root, d, files in os.walk(start):
        to_do = [f for f in files if file_filter(f)]
        if to_do:
            curr = os.path.abspath(os.path.curdir)
            os.chdir(root)
            for file in to_do:
                fpath = os.path.join(root, file)
                try:
                    file_action(file)
                    if return_files:
                        good.append(fpath)
                except Exception as e:
                    if return_files:
                        bad[fpath] = e
                    else:
                        print(f'error on {fpath}: {e}')
            os.chdir(curr)
    if return_files:
        return good, bad

