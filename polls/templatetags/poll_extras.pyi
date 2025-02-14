def get_file_type(value: str) -> str:
    """Returns type of the file"""
    ...

def split(value: str, split_by: str) -> list[str]:
    """Splits the string using entered split_by.

    Args:
        split_by :The character that is going to get used for splitting.
    """
    ...

def split_list(value: list[str], split_by: str) -> list[str]:
    """Splits string in a list using entered split_by.

    Args:
        split_by :The character that is going to used for splitting . Defaults to ,
    """
    ...
