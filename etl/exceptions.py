class CoreException(Exception):
    ctx = ""
    propagate = False

    def __str__(self):
        return self.ctx + " - " + super().__str__()


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
