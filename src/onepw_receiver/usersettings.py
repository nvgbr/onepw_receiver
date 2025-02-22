from pathlib import Path
from types import SimpleNamespace
from typing import Dict

import dotenv
import tomlkit
from tomlkit import TOMLDocument

try:
    import tomllib
except ModuleNotFoundError:
    # import tomli only if tomllib is not installed
    pass  # type:ignore

from .onepassword_item import OnePasswordItem
from .rich_configs import logger


class UserSettings:
    """This class represents a user settings object that is used to read and manipulate settings from a configuration file.

    Attributes:
        settings_file_path (str): The absolute path to the settings file.
        config_dir (str): The directory path where the settings file is located.
        root_path (str): The root path of the project.
        settings_file (str): The path of the settings file.
        settings_file_content (dict): The content of the settings file as a dictionary.

    Methods:
        __init__(absolute_settings_file_path: str): Initializes the UserSettings object.
        _read_settings_file(): Returns the unwrapped settings file content.
        get_section(section: str): Returns the section name from the settings file.
        get_item(item: str, section: str): Returns the value of the specified item in the given section.
        _settings_item_exists(item: str, section: str): Checks if a settings item exists.
        get_onepw_item(settings_item, settings_section): Returns a OnePasswordItem object for the specified item and section.
        set_environment_key(item: str, section: str, key: str): Sets an environment variable using the provided key and the value attribute of the OnePasswordItem.
        _update_secrets_item(): [Not Implemented]
        _write_secrets_file(): [Not Implemented]

    Notes:
        For the path to work, make sure (if you're on Windows) that you either pass the raw absolute settings file path, escape every backslash, or use the normcase method.
        To get the .env variables, use the load_dotenv method before instantiating the UserSettings class.
    """

    absolute_settings_file_path: str
    settings_file: Path
    settings_file_content: dict

    def __init__(self, absolute_settings_file_path: str):
        self.settings_file = Path(absolute_settings_file_path)
        if not Path.exists(self.settings_file):
            logger.error(f"File not found: {self.settings_file}")
            raise FileNotFoundError
        self.settings_file_content = self._read_settings_file()
        logger.debug(f"Instanciated UserSettings with {self.settings_file}")

    def _read_settings_file(self) -> Dict:
        """Returns the unwrapped settings file content."""
        with open(
            self.settings_file,
            "rt",
            encoding="utf-8",
        ) as secrets_file:
            file_content: TOMLDocument = tomlkit.load(secrets_file)
            logger.debug(f"Got file content from {secrets_file}")
            return file_content.unwrap()

    def get_section_from_settings_file(self, section: str):
        """Returns the section name from the settings file."""
        return self.settings_file_content.get(section)

    def get_item(self, item: str, section: str):
        """Get the value of a specified item from a given section in user settings.

        Args:
            item (str): Item to retrieve.
            section (str): Section that contains the item.

        Returns:
            any: Value of the item.
        """
        section = self.get_section_from_settings_file(section)
        return section.get(item)

    def _settings_item_exists(self, item: str, section: str):
        """Checks if a settings item exists."""
        return item in self.settings_file_content.get(section, "")

    def get_onepw_item(
        self, settings_item, settings_section, field_name="credential"
    ):
        """Retrieve an item from OnePassword according to the given settings_item and settings_section.

        Args:
            settings_item (str): Item to fetch from OnePassword.
            settings_section (str): Section to fetch the item from.

        Returns:
            OnePasswordItem: The item fetched from OnePassword.
        """
        from .onepassword_item import OnePasswordItem

        try:
            item = self.get_item(settings_item, settings_section)
            onepw_item = OnePasswordItem(item=item, field_name=field_name)
        except Exception as e:
            logger.error(
                f"{e}\nget_onepw_item(\n    {settings_item=},\n    {settings_section=},\n    {field_name=})"
            )
            logger.error(
                "There was an error retrieving the item from One Password. \n\nDefine the values in your environemnt file if the error persists.",
            )

            onepw_item = SimpleNamespace(key=settings_item.upper(), value=None)
            onepw_item = (
                self.get_value_from_environemnt_file_if_one_pw_server_is_gone(
                    onepw_item
                )
            )
        finally:
            return onepw_item

    def _get_value_from_environemnt_file_if_one_pw_server_is_gone(
        self, onepw_item
    ):
        logger.info(f"Retrieving value from {onepw_item.key=}")
        dotenv_file = dotenv.find_dotenv(filename=".env", usecwd=True)
        logger.debug(f"dotenv found: {dotenv_file=}")
        onepw_item.value = dotenv.get_key(dotenv_file, onepw_item.key)
        logger.debug(f"Key {onepw_item=}")
        return onepw_item

    def set_environment_key(
        self, item: str, section: str, key: str
    ) -> OnePasswordItem:
        """Set a given key in the environment.

        This function retrieves an item from the settings file, sets it as an environment key,
        and returns the item. If an error occurs during the process, it logs the error.

        Args:
            item (str): Name of the item in your settings file.
            section (str): Name of the section where the item is written in your settings file.
            key (str): Name of the environment key you want to set.

        Returns:
            OnePasswordItem
        """
        logger.debug("Setting environment key")
        try:
            onepw_item = self.get_onepw_item(item, section)
            onepw_item.set_key_as_environment_key(key)
            return onepw_item
        except Exception as e:
            logger.error(
                f"{e}\nset_environment_key({item=}, {section=}, {key=})"
            )

    def _update_secrets_item(self):
        return NotImplementedError

    def _write_secrets_file(self):
        return NotImplementedError
