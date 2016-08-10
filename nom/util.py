import os


def abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(os.getcwd(), path)


def get_title(path):
    title, _ = os.path.basename(path).rsplit('.', 1)
    return title


def assets_dir(path):
    """path to the note's assets"""
    title = get_title(path)
    dir = os.path.dirname(path)
    return os.path.join(dir, 'assets', title, '')
