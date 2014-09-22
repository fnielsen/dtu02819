"""Utility functions."""


import os
from os.path import join, splitext


def get_python_files(top='.'):
    """Return all Python files below a given directory.

    Parameters
    ----------
    top : string, option
        Directory name for top directory of search. The default is the
        present working directory.

    Returns
    -------
    files : list
        List with filename including relative path and extension.

    """
    py_files = []
    for root, dirs, files in os.walk(top):
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        for filename in files:
            _, ext = splitext(filename)
            if ext == '.py':
                py_files.append(join(root, filename))
    return py_files
