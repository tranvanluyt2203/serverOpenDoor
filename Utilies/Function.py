import hashlib


def hash(content):
    hashed_content = hashlib.sha256(content.encode()).hexdigest()
    return hashed_content