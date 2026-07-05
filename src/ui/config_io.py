from typing import Dict, List, Tuple


def read_key_value_txt(path: str) -> Dict[str, str]:
    """Parse a `KEY=VALUE`-per-line input config file (same format used by every <mode>/input_parser.py)."""
    with open(path, "r", encoding="UTF8") as input_file:
        lines = input_file.readlines()

    config = {}
    for line in lines:
        key_value = line.strip().split("=")
        if len(key_value) == 2:
            config[key_value[0]] = key_value[1]
    return config


def write_key_value_txt(path: str, pairs: List[Tuple[str, str]]) -> None:
    """Write a `KEY=VALUE`-per-line input config file, preserving the given key order."""
    with open(path, "w", encoding="UTF8") as output_file:
        for key, value in pairs:
            output_file.write(f"{key}={value}\n")
