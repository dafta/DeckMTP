"""
This is the settings module for decky plugins.
"""

from typing import Any

class SettingsManager:
    """
    Handles loading, saving, and editing settings for decky plugins.
    """

    settings: dict[str, str]
    """
    A dictionary containing the settings managed by this SettingsManager.
    """

    path: str
    """
    The path to the settings.json file for this plugin.
    """

    def __init__(self, name: str, settings_directory: str | None = None) -> None:
        """
        Creates a new SettingsManager instance.
        """

    def read(self) -> None:
        """
        Loads the plugin's settings into memory.
        """

    def commit(self) -> None:
        """
        Saves the current settings to the file system.
        """

    def getSetting(self, key: str, default: Any = None) -> Any:
        """
        Gets a specific setting, returning the default value if it isn't found.
        """

    def setSetting(self, key: str, value: Any) -> Any:
        """
        Sets a specific setting to the provided value.
        """
