
import os
from .. import projectproposals


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'fixtures', 'projectproposal.json')


def test_git():
    project = projectproposals.ProjectProposal(filename)
    assert project.git == 'git@github.com:fnielsen/dtu02819.git'
