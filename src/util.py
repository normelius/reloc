



class Item():
    """
    Class to contain a single item,
    which is represented as a file or a folder.
    """
    def __inti__(self):
        self.name = None
        self.path = None
        self.content = None
        self.type_ = None
        self.size = None
        self.mtime = None
        self.suffix = None
