import re
from datetime import datetime


def creation_date_from_full_filename(filename):
    result = re.search('([0-2][0-9]{3}).([0-9]{2}).([0-9]{2})', filename)
    if result != None:
        result = datetime(int(result.group(1)), int(result.group(2)), int(result.group(3)), 23, 59, 59, 999).timestamp()
    return result
