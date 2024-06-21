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
CONFIGS: list[tuple[str,str]] = [
    ("gadget", decky_plugin.DECKY_PLUGIN_SETTINGS_DIR),
    ("umtprd.conf", "/etc/umtprd"),
]


# Helper for systemctl commands
def systemctl(*args: str) -> bool:
    command: list[str] = ["systemctl"]
    command.extend(args)
    return subprocess.run(command, check=False).returncode == 0


# Check if umtprd is running
def is_running() -> bool:
    return systemctl("status", "umtprd")


class Plugin:
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        # Copy configs to correct directory
        for config in CONFIGS:
            input_file = Path(PLUGIN_CONFIGS_DIR, config[0])
            output_folder = Path(config[1])
            output_file = output_folder / config[0]

            if not output_folder.exists():
                output_folder.mkdir()

            if not output_file.exists():
                _ = output_file.write_text(input_file.read_text(encoding="utf-8"))

        # Copy services to correct directory
        for service in SERVICES:
            input_file = Path(PLUGIN_SERVICES_DIR, service)

            # Replace templates in services text
            template = Template(input_file.read_text(encoding="utf-8"))
            substitutions: dict[str, str] = {
                "bindir": PLUGIN_BIN_DIR,
                "scriptsdir": PLUGIN_SCRIPTS_DIR,
                "envfile": decky_plugin.DECKY_PLUGIN_SETTINGS_DIR + "/gadget",
            }

            # Write substituted service
            output_file = Path(decky_plugin.DECKY_PLUGIN_RUNTIME_DIR, service)
            _ = output_file.write_text(
                template.safe_substitute(substitutions), encoding="utf-8"
            )

        # Link services to systemd
        for service in SERVICES:
            service_file = Path(decky_plugin.DECKY_PLUGIN_RUNTIME_DIR, service)
            _ = systemctl("link", str(service_file))

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
            _ = Plugin.start_mtp(self)
        else:
            _ = Plugin.stop_mtp(self)
        return is_running()
