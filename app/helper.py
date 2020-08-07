import json

with open('app/info/names.json') as f:
    character_info_json = json.load(f)

with open('app/info/game-info.json') as f:
    game_info_json = json.load(f)


def get_role_name(role: str) -> str:
    """Gets the actual name of a role from the game-info json.

    Args:
        role (str): The programmatic role name.

    Returns:
        str: The corresponding role name from the game-info json.
    """
    return game_info_json['roles'][role.lower()]['name']


def get_role_description(role: str) -> str:
    """Gets the description for a role.

    Args:
        role (str): The programmatic role name.

    Returns:
        str: The corresponding role description from the game-info json.
    """
    return game_info_json['roles'][role.lower()]['description']


def get_role_action(role: str, is_day: bool) -> str:
    """Gets the action description for a role.

    Args:
        role (str): The programmatic role name.
        is_day (bool): Whether the day or night action description is returned.

    Returns:
        str: The corresponding action description from the game-info json.
    """
    return game_info_json['roles'][role.lower()]['action']['day' if is_day else 'night']


def get_win_message(is_good: bool) -> str:
    """Gets the win description.

    Args:
        is_good (bool): Whether the good guys or bad guys won.

    Returns:
        str: The corresponding win description from the game-info json.
    """
    return game_info_json['win_messages']['good' if is_good else 'bad']
