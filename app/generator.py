import string
import secrets
import json
import random
import math

with open('app/info/names.json') as f:
    character_info_json = json.load(f)


def generate_room_code(size: int) -> str:
    """Generates a room code secret.

    Args:
        size (int): The number of characters in the room code.

    Returns:
        str: The room code.
    """
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(size))


def generate_age() -> int:
    """Generates a random age.

    Returns:
        int: The age.
    """
    return random.randrange(20, 90)


def generate_age_string(age: int) -> str:
    """Generates a string corresponding to an age. Such as, an input of 54 would return 'mid 50s'.

    Args:
        age (int): An age.

    Returns:
        str: An age represented as a string.
    """
    return {1: "early", 5: "mid", 9: "late"}[[1, 5, 9][min(range(len([1, 5, 9])), key=lambda i: abs([1, 5, 9][i]-(age % 10)))]] + ' ' + str(int(age / 10) * 10) + 's'


def generate_gender() -> bool:
    """Returns a random gender. True is male and False is female.

    Returns:
        bool: A gender represented by a bool.
    """
    return bool(random.getrandbits(1))


def generate_gender_pronouns(gender: bool):
    """Gets the pronouns affiliated with a gender

    Args:
        gender (bool): The gender.

    Returns:
        JSON: The pronouns of a gender.
    """
    return character_info_json['pronouns']['he' if gender == 1 else 'she']


def generate_first_name(gender: bool) -> str:
    """Generates a random first name.

    Args:
        gender (bool): The gender the first name should be in.

    Returns:
        str: The first name.
    """
    return random.choice(character_info_json['first_names']['men' if gender == 1 else 'women'])


def generate_last_name() -> str:
    """Generates a random last name.

    Returns:
        str: The last name.
    """
    return random.choice(character_info_json['last_names'])
