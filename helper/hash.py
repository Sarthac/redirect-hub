import hashlib


def get_user_id_hash(input: str) -> str:
    return hashlib.sha3_256(input.encode("utf-8")).hexdigest()


def check_userid(input_hash: str, input: str) -> bool:
    return input_hash == get_user_id_hash(input)


def get_hash(input: str) -> str:
    return hashlib.sha3_256(input.encode("utf-8")).hexdigest()


def check_hash(input_hash: str, input: str) -> bool:
    return input_hash == get_hash(input)
