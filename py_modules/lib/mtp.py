from pathlib import Path
import subprocess

from settings import SettingsManager
import decky

from . import utils
from . import systemctl


class Mtp:
    # Services to enable
    services: list[str] = [
        "umtprd.service",
        "usbgadget-func-mtp.service",
    ]

    # MTP settings
    settings: SettingsManager

    def __init__(self):
        # Init settings
        Mtp.settings = SettingsManager(
            name="mtp", settings_directory=decky.DECKY_PLUGIN_SETTINGS_DIR
        )
        Mtp.settings.read()

        if Mtp.settings.getSetting("enabled", False):
            Mtp.enable(self)

    def enable(self):
        _ = systemctl.enable(self.services)

        # Copy umtprd.conf to the correct location
        Mtp.deploy_umtprd_conf(self)

    def disable(self):
        _ = systemctl.disable(self.services)

        # Delete umtprd.conf from /etc
        umtprd_conf = Path("/etc/umtprd/umtprd.conf")
        umtprd_conf.unlink(missing_ok=True)
        if umtprd_conf.parent.exists():
            umtprd_conf.parent.rmdir()

    def is_enabled(self) -> bool:
        for service in self.services:
            if not systemctl.is_enabled(service):
                return False

        return True

    def toggle(self):
        if Mtp.is_enabled(self):
            Mtp.settings.setSetting("enabled", False)
            Mtp.disable(self)
        else:
            Mtp.settings.setSetting("enabled", True)
            Mtp.enable(self)

    # Deploy umtprd.conf to the correct location
    def deploy_umtprd_conf(self):
        input_file = Path(decky.DECKY_PLUGIN_SETTINGS_DIR, "umtprd.conf")
        output_file = Path("/etc/umtprd/umtprd.conf")

        # Create the folder if it doesn't exist
        if not output_file.parent.exists():
            output_file.parent.mkdir()

        # Copy the file
        utils.copy_template(input_file, output_file)

    # Add folder to umtprd
    def umtprd_add_folder(self, folder: Path, name: str) -> bool:
        # Check if the folder exists
        if not folder.exists():
            return False

        # The command to add the folder
        command: list[str] = [
            utils.PLUGIN_BIN_DIR + "/umtprd",
            "-cmd:addstorage:" + str(folder) + ' "' + name + '"' + " rw",
        ]

        # Run the command
        return subprocess.run(command, check=False).returncode == 0

    # Add SD card folders
    def add_sdcard_folders(self):
        for folder in Path("/run/media").iterdir():
            if folder.is_mount():
                _ = Mtp.umtprd_add_folder(self, folder, folder.name)
