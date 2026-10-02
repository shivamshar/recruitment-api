from pwdlib import PasswordHash


# PasswordHash.recommended() creates a password
# hashing configuration using modern recommended settings.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:


    return password_hash.hash(password)


#we will add login later