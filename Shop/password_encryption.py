from passlib.context import CryptContext
pow_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def password_encryption(password):
    hash = pow_context.hash(password)
    return hash
def check_password_match(user_password, hash_db_password):
    pow_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    check = pow_context.verify(user_password, hash_db_password)
    if check:
        return True
    else:
        return False

