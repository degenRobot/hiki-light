import random


def generate_random_hexstring(length: int = 32) -> str:
    return random.randbytes(length).hex()
