"""
Reloc
@ 2020, Anton Normelius
Simple file transfer package between client and server.
MIT License.
"""

class Item():
    """
    Information about a single file/folder.
    Used when transfering the files to the server.
    """
    def __init__(self):
        self.name = None
        self.path = None
        self.content = None
        self.type_ = None
        self.size = 0
        self.mtime = 0
        self.suffix = None

    def __eq__(self, other):
        """
        Method to compare objects by path.
        """
        if self.path == other.path:
            return True
