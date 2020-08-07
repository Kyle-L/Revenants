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


def get_result_message_general(result: str) -> str:
    """Gets a general result message.

    Args:
        result (str): The programmatic general result name.

    Returns:
        str: The corresponding general result message from the game-info json.
    """
    return game_info_json['result_messages_general'][result.lower()]


def get_result_message_private(result: str) -> str:
    """Gets a private result message.

    Args:
        result (str): The programmatic private result name.

    Returns:
        str: The corresponding private result message from the game-info json.
    """
    return game_info_json['result_messages_private'][result.lower()]


def get_player_end_status(status: bool) -> str:
    """Gets string for a player's end status.

    Args:
        result (str): The programmatic status of a player.

    Returns:
        str: The corresponding end status from the game-info json.
    """
    return game_info_json[player_end_status]['alive' if status else 'dead']


def get_win_message(is_good: bool) -> str:
    """Gets the win description.

    Args:
        is_good (bool): Whether the good guys or bad guys won.

    Returns:
        str: The corresponding win description from the game-info json.
    """
    return game_info_json['win_messages']['good' if is_good else 'bad']
