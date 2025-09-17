from utils.security import get_current_user

def get_optional_user():
    return get_current_user(optional=True)