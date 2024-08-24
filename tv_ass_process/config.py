import json
from typing import Union

from .constants import MergeMode


class Config:
    def __init__(self, arg: Union[str, dict]):
        if isinstance(arg, str):
            self.init_from_file(arg)
        elif isinstance(arg, dict):
            self.init_from_dict(arg)
        else:
            raise TypeError("Invalid argument type")

    def init_from_file(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as file:
            local_config = json.load(file)
        self.init_from_dict(local_config)

    def init_from_dict(self, user_config: dict):
        self.merge = MergeMode(user_config.get("merge", "auto"))
        self.clean_mode = user_config.get("clean_mode", True)
        self.actor = user_config.get("actor", False)
        self.output_format = user_config.get("output_format", "txt")
        self.add_spaces = user_config.get("add_spaces", False)
        self.ending_char = user_config.get("ending_char", "")
        self.adjust_repeated_syllables = user_config.get(
            "adjust_repeated_syllables", True
        )
        self.output_path = None
