class CoreException(Exception):
    ctx = ""
    propagate = False

    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return self.ctx + " - " + self.msg


class XmlInvalidStructure(CoreException):
    ctx = "Invalid XML structure"
    propagate = False


class ConvertException(CoreException):
    ctx = "Unknown error. cannot convert xml to data object"
    propagate = False


class RepoException(CoreException):
    """
    Note: Ofcourse in a real scenario we need more specific exceptions, for this task it is just enough!
    """
    ctx = "repo error"
    propagate = True
