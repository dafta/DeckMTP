from pathlib import Path
import subprocess

import decky_plugin

from . import utils
from . import systemctl

# Services to enable
services: list[str] = [
    "umtprd.service",
    "usbgadget-func-mtp.service",
]


def enable():
    _ = systemctl.enable(services)

    # Copy umtprd.conf to the correct location
    deploy_umtprd_conf()


def disable():
    _ = systemctl.disable(services)

    # Delete umtprd.conf from /etc
    umtprd_conf = Path("/etc/umtprd/umtprd.conf")
    umtprd_conf.unlink(missing_ok=True)
    if umtprd_conf.parent.exists():
        umtprd_conf.parent.rmdir()


# Deploy umtprd.conf to the correct location
def deploy_umtprd_conf():
    input_file = Path(decky_plugin.DECKY_PLUGIN_SETTINGS_DIR, "umtprd.conf")
    output_file = Path("/etc/umtprd/umtprd.conf")

    # Create the folder if it doesn't exist
    if not output_file.parent.exists():
        output_file.parent.mkdir()

    # Copy the file
    utils.copy_template(input_file, output_file)


# Add folder to umtprd
def umtprd_add_folder(folder: Path, name: str) -> bool:
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
def add_sdcard_folders():
    for folder in Path("/run/media").iterdir():
        if folder.is_mount():
            _ = umtprd_add_folder(folder, folder.name)
