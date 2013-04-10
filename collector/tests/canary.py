"""
Simple smoke tests that serve as a "canary" for this codebase...
"""

# Ugly hack to allow absolute import from the root folder
# whatever its name is. Please forgive the heresy.
if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir_

    path.append(dir_(path[0]))
    __package__ = "tests"
# So what street corner did that I pick that up from?
#
#   Evpok mentioned it on StackOverflow and I thought it was better than other
#   ideas I had for getting code importable for testing and I don't know that
#   these scripts will be "a module" until a framework is used.
#
#   In short, thanks to Evpok - it'll help get me testing this code.
#
# url: http://stackoverflow.com/questions/6323860/
#           sibling-package-imports/6466139#6466139

from provenance_agent import ProvTuple


def test_init():
    """
    Verify that code from tardis-collector can be imported...
    """
    prov = ProvTuple(9090909090, 'DE', 'view', 'list-dir', 'tester',
                    '10.0.0.1')
    return prov is not None