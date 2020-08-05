import string
import secrets
import json
import random
import math

with open('app/info/names.json') as f:
  character_info_json = json.load(f)

with open('app/info/game-info.json') as f:
  game_info_json = json.load(f)


def generate_room_code(size) -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(size))


def generate_age() -> int:
    return random.randrange(20, 90)


def generate_age_string(age) -> str:
    return {1: "early", 5: "mid", 9: "late"}[[1, 5, 9][min(range(len([1, 5, 9])), key=lambda i: abs([1, 5, 9][i]-(age % 10)))]] + ' ' + str(int(age / 10) * 10) + 's'


def generate_gender() -> bool:
    return bool(random.getrandbits(1))


def generate_gender_pronouns(gender):
    return character_info_json['pronouns']['he' if gender == 1 else 'she']


def generate_first_name() -> str:
    return random.choice(character_info_json['first_names']['men' if gender == 1 else 'women'])


def generate_last_name() -> str:
    return random.choice(character_info_json['last_names'])


def generate_occupation() -> str:
    return random.choice(character_info_json['occupations'])


def generate_retired_state(age):
    return '' if age < 40 else ('Retired' if random.randrange(0, 100) < (math.sin(age * 0.0386 + 3.2) * 100 + 100) else '')


def get_role_name(role: str) -> str:
    return game_info_json['roles'][role.lower()]['name']


def get_role_description(role: str) -> str:
    return game_info_json['roles'][role.lower()]['description']

def get_role_action(role: str, is_day: bool) -> str:
    return game_info_json['roles'][role.lower()]['action']['day' if is_day else 'night']

def get_win_message(is_good: bool) -> str:
    return game_info_json['win_messages']['good' if is_good else 'bad']