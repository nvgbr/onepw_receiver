# coding=utf-8
import sys
import os
from typing import Dict, Optional
from dataclasses import dataclass, InitVar, field

from dotenv import load_dotenv
from onepasswordconnectsdk.client import (
    Client,
    new_client_from_environment,
    )
from httpx import ConnectTimeout
from onepw_receiver.rich_configs import logger

# Load environment variables
load_dotenv()


@dataclass
class OnePasswordItem:
    """Class representing an item in 1Password vault.

    This class provides methods to retrieve field values from 1Password items
    and set environment variables with those values.

    Attributes:
        vault_name (str): The name of the 1Password vault.
        vault_id (str): The ID of the 1Password vault.
        item (str): The ID of the 1Password item.
        field_name (str): The name of the field of the 1Password item.
        section (str): The name of the section.
        value (str): The value of the field.

    Methods:
        __init__(item_id, field_name, section=None):
            Initializes a new instance of the OnePasswordItem class.

        set_environment_key(key: str):
            Sets an environment variable using the provided key and the instance's 'value' attribute.
    """

    # Load environment variables
    load_dotenv()

    item: str
    field_name: str
    vault_name: Optional[str]
    section: Optional[str]
    value: str
    vault_id: str

    # Creating client using OP_CONNECT_TOKEN and OP_CONNECT_HOST env vars
    client: Client = new_client_from_environment()


    def __init__(self, item, field_name='credentials', section=None, vault_name=None):
        self.item = item
        self.field_name = field_name
        self.section = section
        self.vault_name = os.getenv('OP_VAULT') if vault_name is None else vault_name
        self.vault_id = self._get_vault_id()
        self.value = self._get_field_value()


    def _get_vault_id(self) -> str:
        """Return the ID of the specified vault name.
        Args:
           vault_name (str): The name of the vault whose ID is to be returned.
        Returns:
           str: The ID of the specified vault.
        Raises:
           Exception: If there is an error while retrieving the vault dictionary.
        """
        vault_dict = self._get_vault_dict()
        if not vault_dict:
            return
        return vault_dict.get(self.vault_name, "")


    def _get_field_value(self):
        """Return the value of a specified field for the specified 1Password item.
        Args:
           item (str): The name or ID of the 1Password item to retrieve the
           field value from.
           vault (str): The name or ID of the vault where the item is stored.
           field_name (str): The name of the field whose value is to be retrieved.
           section (Optional[str]): The name of the section where the item is
           located.
        Returns:
           The value of the specified field for the specified 1Password item.
        Raises:
           Exception: If there is an error while retrieving the 1Password item
           or the field value.
        """
        return self._get_item().get(self.field_name, self.section)


    def _get_item(self):
        onepw_item = self.client.get_item(self.item, self.vault_id)
        return {field.label: field.value for field in onepw_item.fields}


    def _get_vaults(self):
        try:
            return OnePasswordItem.client.get_vaults()
        except ConnectTimeout as e:
            logger.error(e)
            print(f"Connection timed out. Please try again or provide the necessary credential value in an environment variable.")
            return


    def _get_vault_dict(self) -> Dict[str, str]:
        """Return a dictionary of available 1Password vault names and their IDs.
        Returns:
           dict: A dictionary of vault names and their IDs.
        Raises:
           Exception: If there is an error while retrieving vaults.
        """
        vaults = self._get_vaults()
        if not vaults:
            return
        vault_dict = {self.item.name: self.item.id for self.item in vaults}
        return vault_dict

    def set_environment_key(self, key: str):
        """Set an environment variable using provided key and instance 'value' attribute.

        With the provided key, this method sets an environment variable using the 'value' attribute of the OnePasswordItem class instance.

        Args:
            key (str): The key for the desired environment variable.

        Returns:
            None

        Example:
            item = OnePasswordItem()
            item.set_environment_key('MY_VARIABLE')
            None

        Note:
            The 'value' attribute of the 'OnePasswordItem' instance is assumed to be set before this method is called.
            If 'value' is not set, behavior is undefined.
        """
        env_key = key.upper()
        try:
            os.environ[env_key] = self.value
            logger.info(f"Environment Variable: '{key}' has been set.")
        except Exception as e:
            logger.error(f"{e}\nEnvironment Variable: '{key}' could not be set.")
