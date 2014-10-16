"""Handle projectproposals.

Students hand in project proposals in a predefined JSON format where
they specify title, a list of group members, git repository,
description and a list of modules.

Example
-------
>>> JSON = '''
{
  "title": "Data mining of Data Mining using Python",
  "members": [
    { "name": "Finn Aarup Nielsen",
      "study_number": "faan"
    }
  ],
  "git": "git@github.com:fnielsen/dtu02819.git",
  "description": "Data mining of data from the DTU course 02819",
  "modules": ["nltk", "csv", "django", "pandas", "gensim", "sklearn"]
}'''

"""


import codecs
import json
import os
import pandas as pd
import re


FILENAME_PROJECTPROPOSAL = 'projectproposal.json'


class ProjectProposal(object):

    """Represent one projectproposal."""

    def __init__(self, filename=FILENAME_PROJECTPROPOSAL):
        """Read and check project proposal from file or directory name."""
        self.fields = ['title', 'members', 'git', 'description',
                       'modules']
        self.title = ""
        self.members = []
        self.git = ""
        self.description = ""
        self.modules = []
        self.raw = ""
        if os.path.isfile(filename):
            self.read(filename)
        elif os.path.isdir(filename):
            self.read_from_dir(filename)
        else:
            raise IOError("No such file or directory")
        self.check_members()

    def read_from_dir(self, dirname, filename=FILENAME_PROJECTPROPOSAL):
        """Set fields from a directory with a JSON file."""
        tentative_filename = os.path.join(dirname, filename)
        if os.path.isfile(tentative_filename):
            self.read(tentative_filename)
        else:
            filenames = os.listdir(dirname)
            if len(filenames) == 1:
                self.read(os.path.join(dirname, filenames[0]))
            else:
                raise IOError('Missing file in directory')

    def read(self, filename):
        """Set fields from JSON file."""
        with codecs.open(filename, encoding='utf-8') as fid:
            self.raw = fid.read()
        data = json.loads(self.raw)
        for field in self.fields:
            setattr(self, field, data[field])
        self.fix_modules()

    def check_members(self):
        """Check that 'members' field have correct subfields."""
        if len(self.members) < 1:
            raise ValueError('Number of members should be larger than zero')
        for member in self.members:
            if 'name' not in member:
                raise ValueError("Member should have 'name'")
            if 'study_number' not in member:
                raise ValueError("Member should have 'study_number'")

    def fix_modules(self):
        """Change modules to list of strings if string."""
        if not hasattr(self, 'modules'):
            self.modules = []
        if isinstance(self.modules, basestring):
            self.modules = re.findall('\W+', self.modules, flags=re.UNICODE)

    def keys(self):
        """Return project proposal attributes as keys."""
        return self.fields

    def items(self):
        """Return project proposal attributes and values as tuples."""
        return [(key, getattr(self, key)) for key in self.keys()]

    def values(self):
        """Return project proposal attributes values."""
        return [getattr(self, key) for key in self.keys()]


class ProjectProposals(object):

    """Represent a list of proposals."""

    def __init__(self, dirname='.'):
        """Initialize and read project proposals under a given directory."""
        self._proposals = []
        self.read(dirname=dirname)

    def read(self, dirname):
        """Read all project proposal files under a given directory."""
        subdirnames = os.listdir(dirname)
        for subdirname in subdirnames:
            if re.match('s\d+', subdirname) or '(faan)' == subdirname:
                proposal = {'uploader': subdirname, 'status': 'ok'}
                try:
                    proposal.update(ProjectProposal(subdirname).items())
                except (KeyError, ValueError) as err:
                    proposal['status'] = str(err)
                self._proposals.append(proposal)

    def get_titles(self):
        """Return all titles."""
        return [proposal.get('title', '') for proposal in self._proposals]

    def to_status_df(self, columns=('uploader', 'title', 'status')):
        """Convert proposals to dataframe with status."""
        return pd.DataFrame([[proposal.get(column, '') for column in columns]
                             for proposal in self._proposals], columns=columns)

    def to_modules_df(self):
        """Convert module description to Pandas dataframe."""
        # Columns and rows
        modules = set()
        for proposal in self._proposals:
            modules |= set(proposal.get('modules', []))
        index = [proposal['uploader'] for proposal in self._proposals]

        # Set elements of dataframe
        dataframe = pd.DataFrame(index=index, columns=modules)
        for proposal in self._proposals:
            for module in dataframe.columns:
                dataframe.ix[proposal['uploader'], module] = \
                    module in proposal.get('modules', [])
        return dataframe

    def to_html(self):
        """Convert data to an HTML string."""
        return (self.to_status_df().to_html() + '\n<br><br>\n' +
                self.to_modules_df().to_html())
