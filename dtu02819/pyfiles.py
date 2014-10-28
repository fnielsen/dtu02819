"""Perform various checks on Python files."""


import os
import pandas as pd
import pep257
from pylint import epylint as lint
import re


class CheckError(Exception):

    """Exception for file checking."""

    pass


class PyFile(dict):

    """Representation of a Python file.

    Example
    -------
    >>> pyfile = PyFile(__file__)
    >>> 'pyfiles.py' in pyfile['Filename']
    True

    >>> pyfile.get_pylint_rating() > 9.5
    True

    """

    def __init__(self, filename, check_all=True):
        dict.__init__(self)
        self['Filename'] = filename
        self._pattern_pylint_rating = \
            re.compile(r'Your code has been rated at (\d+\.\d{2})')
        if check_all:
            self.check_all()

    def run_pep257(self):
        """Run and return output from pep257 tool."""
        return pep257.check([self['Filename']])

    def run_pylint(self):
        """Run pylint on file and return output."""
        (pylint_stdout, pylint_stderr) = lint.py_run(self['Filename'],
                                                     return_std=True,
                                                     script='pylint')
        if pylint_stderr:
            msg = pylint_stderr.read().strip()
            if msg != 'No config file found, using default configuration':
                raise CheckError(msg)
        return pylint_stdout.read()

    def get_pylint_rating(self):
        """Get the pylint rating for the file."""
        output = self.run_pylint()
        matches = self._pattern_pylint_rating.findall(output)
        if len(matches) == 1:
            return float(matches[0])
        elif len(matches) > 1:
            raise CheckError('Too many matches in pylint rating')
        else:
            raise CheckError('Did not match pylint rating')

    def get_number_of_lines(self):
        """Return total number of lines in file."""
        return len(open(self['Filename']).read().strip().split('\n'))

    def get_number_of_pep257_issues(self):
        """Return number of issues that the pepe257 reports."""
        return len(list(self.run_pep257()))

    def check_all(self):
        """Compute all characteristics of a file."""
        self['Number of lines'] = self.get_number_of_lines()
        self['Pylint rating'] = self.get_pylint_rating()
        self['Number of pep257 issues'] = self.get_number_of_pep257_issues()

    def to_series(self):
        """Return data about Python file as Pandas Series."""
        return pd.Series(self)


class PyFiles(list):

    """Represent data about a set of Python files in a list."""

    def __init__(self, dirname='.'):
        list.__init__(self)
        self.top_dir = dirname
        self.read_py_files()

    @staticmethod
    def is_py_filename(filename):
        """Check is file is a .py file.

        Example
        -------
        >>> PyFiles.is_py_filename('test.py')
        True

        """
        return filename.endswith('.py')

    def py_filenames(self):
        """Return generator for .py files by walking directories."""
        for dirpath, _, filenames in os.walk(self.top_dir):
            for filename in filenames:
                filename_with_path = os.path.join(dirpath, filename)
                if self.is_py_filename(filename_with_path):
                    yield filename_with_path

    def read_py_files(self):
        """Read and setup data about py files."""
        for py_filename in self.py_filenames():
            self.append(PyFile(py_filename))

    def total_number_of_lines(self):
        """Return the sum of the number of lines."""
        return sum([pyfile['Number of lines'] for pyfile in self])

    def min_pylint_rating(self):
        """Return the minimum pylint rating across files."""
        return min([pyfile['Pylint rating'] for pyfile in self])    

    def max_number_of_pep257_issues(self):
        """Return the maximum number of pep257 issues across files."""
        return max([pyfile['Number of pep257 issues'] for pyfile in self])

    def to_df(self):
        """Convert data to Pandas DataFrame."""
        return pd.DataFrame(self)

    def to_series(self):
        results = {
            'Total number of lines': self.total_number_of_lines(),
            'Min pylint rating': self.min_pylint_rating(),
            'Max number of pep257 issues': self.max_number_of_pep257_issues()
            }
        return pd.Series(results)

