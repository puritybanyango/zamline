# Owner: Helen Mezgebe
# Feature: User Registration and Secure Access


def _password_hasher():
    from pwdlib import PasswordHash

    return PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hasher().hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hasher().verify(password, password_hash)
