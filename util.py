
def human_readable(size_bytes):
    """
    Convert a file size in bytes to a human-readable format
    """
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f'{size_bytes:.2f} {units[i]}'