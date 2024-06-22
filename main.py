from pathlib import Path
import subprocess
import sys

from string import Template

import decky_plugin


# append py_modules to PYTHONPATH
sys.path.append(str(Path().cwd() / "py_modules"))

# Constants to important folders
PLUGIN_BIN_DIR: str = decky_plugin.DECKY_PLUGIN_DIR + "/bin"
PLUGIN_SERVICES_DIR: str = PLUGIN_BIN_DIR + "/services"
PLUGIN_SCRIPTS_DIR: str = PLUGIN_BIN_DIR + "/scripts"
PLUGIN_CONFIGS_DIR: str = PLUGIN_BIN_DIR + "/configs"

# Services to install
SERVICES: list[str] = [
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


# Helper for systemctl commands
def systemctl(*args: str) -> bool:
    command: list[str] = ["systemctl"]
    command.extend(args)
    return subprocess.run(command, check=False).returncode == 0


# Check if umtprd is running
def is_running() -> bool:
    return systemctl("status", "umtprd")


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


# Deploy umtprd.conf to the correct location
def deploy_umtprd_conf():
    input_file = Path(decky_plugin.DECKY_PLUGIN_SETTINGS_DIR, "umtprd.conf")
    output_file = Path("/etc/umtprd/umtprd.conf")

    # Create the folder if it doesn't exist
    if not output_file.parent.exists():
        output_file.parent.mkdir()

    # Copy the file
    copy_template(input_file, output_file)


class Plugin:
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        # Copy configs to correct directory
        for config in CONFIGS:
            input_file = Path(PLUGIN_CONFIGS_DIR, config)
            output_file = Path(decky_plugin.DECKY_PLUGIN_SETTINGS_DIR, config)

            if not output_file.exists():
                copy_template(input_file, output_file)

        # Copy services to correct directory
        for service in SERVICES:
            input_file = Path(PLUGIN_SERVICES_DIR, service)
            output_file = Path(decky_plugin.DECKY_PLUGIN_RUNTIME_DIR, service)

            # Define substitutions
            substitutions: dict[str, str] = {
                "bindir": PLUGIN_BIN_DIR,
                "scriptsdir": PLUGIN_SCRIPTS_DIR,
                "envfile": decky_plugin.DECKY_PLUGIN_SETTINGS_DIR + "/gadget",
            }

            # Replace templates and copy file
            copy_template(input_file, output_file, substitutions)

        # Copy umtprd.conf to the correct location
        deploy_umtprd_conf()

        # Link services to systemd
        for service in SERVICES:
            service_file = Path(decky_plugin.DECKY_PLUGIN_RUNTIME_DIR, service)
            _ = systemctl("enable", str(service_file))

    # Function called first during the unload process,
    # utilize this to handle your plugin being removed
    async def _unload(self):
        _ = await Plugin.stop_mtp(self)

    # Check if umtprd is running
    async def is_running(self) -> bool:
        return is_running()

    # Check if Dual-Role Device is enabled in BIOS
    async def is_drd_enabled(self) -> bool:
        try:
            with subprocess.Popen(
                "lsmod | grep dwc3", shell=True, stdout=subprocess.PIPE
            ) as p:
                assert p.stdout is not None
                result = p.stdout.read().strip()
        except Exception:
            return False
        return bool(result)

    # Start MTP
    async def start_mtp(self) -> bool:
        return systemctl("start", "usb-gadget.target")

    # Stop MTP
    async def stop_mtp(self) -> bool:
        return systemctl("stop", "gadget-init.service")

    # Toggle MTP
    async def toggle_mtp(self) -> bool:
        if not is_running():
            _ = await Plugin.start_mtp(self)
        else:
            _ = await Plugin.stop_mtp(self)
        return is_running()
