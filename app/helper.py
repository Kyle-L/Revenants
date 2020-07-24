import string, secrets

def generate_room_code (size):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(size))
    