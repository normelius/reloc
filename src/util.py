"""
@ 2020, Anton Normelius.
Simple file transfer library between client and server,
based on the socket library.
MIT License.
"""

class Item():
    """
    Class to contain a single item,
    which is represented as a file or a folder.
    """
    def __init__(self):
        self.name = None
        self.path = None
        self.content = None
        self.type_ = None
        self.size = None
        self.mtime = None
        self.suffix = None
