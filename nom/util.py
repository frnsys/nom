import os
import hashlib


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

def get_file_hash(path):
   # make a hash object
   h = hashlib.sha1()

   # open file for reading in binary mode
   with open(path, 'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()
