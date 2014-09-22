"""Perform various checks on Python files."""


from pylint import epylint as lint
import re
import pandas as pd


class CheckError(Exception):
    pass


class PythonFile(dict):
    
    """Representation of a Python file.

    Example
    -------
    >>> pyfile = PythonFile('utils.py')
    >>> pyfile['Filename']
    'utils.py'

    >>> pyfile.get_pylint_rating()
    10.0

    """

    def __init__(self, filename):
        self['Filename'] = filename
        self._pattern_pylint_rating = \
            re.compile(r'Your code has been rated at (\d+\.\d{2})')

    def run_pylint(self):
        """Run pylint on file and return output."""
        (pylint_stdout, pylint_stderr) = lint.py_run(self['Filename'], 
                                                     return_std=True,
                                                     script='pylint')
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
        return len(open(self['Filename']).read().strip().split('\n'))

    def check_all(self):
        self['Number of lines'] = self.get_number_of_lines()
        self['Pylint rating'] = self.get_pylint_rating()

    def to_series(self):
        """Return data about Python file as Pandas Series."""
        return pd.Series(self)


class PythonFiles(list):
    def __init__(self):
        pass
