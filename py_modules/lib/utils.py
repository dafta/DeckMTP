from pathlib import Path
from string import Template

import decky

# Constants to important folders
PLUGIN_BIN_DIR: str = decky.DECKY_PLUGIN_DIR + "/bin"
PLUGIN_SERVICES_DIR: str = PLUGIN_BIN_DIR + "/services"
PLUGIN_NETWORKS_DIR: str = PLUGIN_BIN_DIR + "/networks"
PLUGIN_SCRIPTS_DIR: str = PLUGIN_BIN_DIR + "/scripts"
PLUGIN_CONFIGS_DIR: str = PLUGIN_BIN_DIR + "/configs"

# Services to install
services: list[str] = [
    "gadget-bind.service",
    "gadget-init.service",
    "gadget-start.service",
    "umtprd.service",
    "usbgadget-func-ecm.service",
    "usbgadget-func-eem.service",
    "usbgadget-func-geth.service",
    "usbgadget-func-mtp.service",
    "usbgadget-func-ncm.service",
    "usbgadget-func-rndis.service",
]

# Networks to install
networks: list[str] = ["usb0.network"]

# Configs to install, and the folders to install them into
configs: list[str] = [
    "gadget",
    "umtprd.conf",
]


# Install plugin files
def install():
    # Copy configs to correct directory
    for config in configs:
        input_file = Path(PLUGIN_CONFIGS_DIR, config)
        output_file = Path(decky.DECKY_PLUGIN_SETTINGS_DIR, config)

        if not output_file.exists():
            copy_template(input_file, output_file)

    # Copy services to correct directory
    for service in services:
        input_file = Path(PLUGIN_SERVICES_DIR, service)
        output_file = Path(decky.DECKY_PLUGIN_RUNTIME_DIR, service)

        # Define substitutions
        substitutions: dict[str, str] = {
            "bindir": PLUGIN_BIN_DIR,
            "scriptsdir": PLUGIN_SCRIPTS_DIR,
            "envfile": decky.DECKY_PLUGIN_SETTINGS_DIR + "/gadget",
        }

        # Replace templates and copy file
        copy_template(input_file, output_file, substitutions)

    # Copy networks to correct directory
    for network in networks:
        input_file = Path(PLUGIN_NETWORKS_DIR, network)
        output_file = Path(decky.DECKY_PLUGIN_RUNTIME_DIR, network)

        # Copy network files
        copy_template(input_file, output_file)


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
