import hashlib

def row_hashing(row):
    row_str = "|".join(map(str, row.values))  # concat values into a string
    return hashlib.md5(row_str.encode()).hexdigest()