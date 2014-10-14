"""Handle projectproposals."""


import codecs
import json
import os
import pandas as pd
import re


FILENAME_PROJECTPROPOSAL = 'projectproposal.json'


class ProjectProposal(object):
    """Represent one projectproposal."""

    def __init__(self, filename=FILENAME_PROJECTPROPOSAL):
        self.fields = ['title', 'members', 'git', 'description', 'modules']
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
        with codecs.open(filename, encoding='utf-8') as f:
            self.raw = f.read()
        data = json.loads(self.raw)
        for field in self.fields:
            setattr(self, field, data[field])

    def check_members(self):
        """Check that 'members' field have correct subfields."""
        if len(self.members) < 1:
            raise ValueError('Number of members should be larger than zero')
        for member in self.members:
            if 'name' not in member:
                raise ValueError("Member should have 'name'")
            if 'study_number' not in member:
                raise ValueError("Member should have 'study_number'")

    def keys(self):
        return self.fields

    def items(self):
        return [(key, getattr(self, key)) for key in self.keys()]

    def values(self):
        return [getattr(self, key) for key in self.keys()]
    

class ProjectProposals(object):
    """Represent a list of proposals."""
    
    def __init__(self, dirname='.'):
        self._proposals = []
        self.read(dirname=dirname)

    def read(self, dirname):
        subdirnames = os.listdir(dirname)
        for subdirname in subdirnames:
            if re.match('s\d+', subdirname ):
                proposal = {'uploader': subdirname, 'status': 'ok'}
                try:
                    proposal.update(ProjectProposal(subdirname).items())
                except (KeyError, ValueError) as e:
                    proposal['status'] = str(e)
                self._proposals.append(proposal)

    def get_titles(self):
        """Return all titles."""
        return [proposal.get('title', '') for proposal in self._proposals]
            
    def to_status_df(self, columns=['uploader', 'title', 'status']):
        """Convert proposals to dataframe with status."""
        return pd.DataFrame([[proposal.get(column, '') for column in columns] 
                             for proposal in self._proposals], columns=columns)
                                       
    def to_modules_df(self):
        """Convert module description to dataframe."""
        # Columns and rows        
        modules = set()
        for proposal in self._proposals:
            modules |= set(proposal.get('modules', []))
        index = [proposal['uploader'] for proposal in self._proposals]

        # Set elements of dataframe
        df = pd.DataFrame(index=index, columns=modules)
        for proposal in self._proposals:
            for module in df.columns:
                df.ix[proposal['uploader'], module] = module in proposal.get('modules', [])
        return df
        
    def to_html(self):
        return (self.to_status_df().to_html() + '\n<br><br>\n' + 
                self.to_modules_df().to_html())
