from pathlib import Path
from string import Template

import decky_plugin

from . import systemctl

# Constants to important folders
PLUGIN_BIN_DIR: str = decky_plugin.DECKY_PLUGIN_DIR + "/bin"
PLUGIN_SERVICES_DIR: str = PLUGIN_BIN_DIR + "/services"
PLUGIN_SCRIPTS_DIR: str = PLUGIN_BIN_DIR + "/scripts"
PLUGIN_CONFIGS_DIR: str = PLUGIN_BIN_DIR + "/configs"

# Services to install
SERVICES: list[str] = [
    "gadget-bind.service",
    "gadget-init.service",
    "gadget-start.service",
    "umtprd.service",
    "usbgadget-func-mtp.service",
]

# Configs to install, and the folders to install them into
CONFIGS: list[str] = [
    "gadget",
    "umtprd.conf",
]


# Check if umtprd is running
def is_running() -> bool:
    return systemctl.status("umtprd")


# Read file and write to another path, optionally replace templates
def copy_template(
    input_file: Path, output_file: Path, substitutions: dict[str, str] | None = None
):
    # Read the file
    text = input_file.read_text(encoding="utf-8")

    # Replace templates in services text
    if substitutions is not None:
        template = Template(text)
        text = template.safe_substitute(substitutions)

    _ = output_file.write_text(text, encoding="utf-8")
