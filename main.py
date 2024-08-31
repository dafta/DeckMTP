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


# Helper for systemctl commands
class Systemctl:
    @staticmethod
    def status(service: str) -> bool:
        command: list[str] = ["systemctl", "status"]
        command.append(service)
        return subprocess.run(command, check=False).returncode == 0

    @staticmethod
    def enable(services: list[str]) -> bool:
        command: list[str] = ["systemctl", "enable"]

        for service in services:
            command.append(decky_plugin.DECKY_PLUGIN_RUNTIME_DIR + "/" + service)

        return subprocess.run(command, check=False).returncode == 0

    @staticmethod
    def disable(services: list[str]) -> bool:
        command: list[str] = ["systemctl", "disable"]
        command.extend(services)
        return subprocess.run(command, check=False).returncode == 0

    @staticmethod
    def start(*args: str) -> bool:
        command: list[str] = ["systemctl", "start"]
        command.extend(args)
        return subprocess.run(command, check=False).returncode == 0

    @staticmethod
    def stop(*args: str) -> bool:
        command: list[str] = ["systemctl", "stop"]
        command.extend(args)
        return subprocess.run(command, check=False).returncode == 0


# Check if umtprd is running
def is_running() -> bool:
    return Systemctl.status("umtprd")


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


class MTP:
    # Services to enable
    services: list[str] = [
        "umtprd.service",
        "usbgadget-func-mtp.service",
    ]

    @staticmethod
    def enable():
        _ = Systemctl.enable(MTP.services)

        # Copy umtprd.conf to the correct location
        MTP.deploy_umtprd_conf()

    @staticmethod
    def disable():
        _ = Systemctl.disable(MTP.services)

        # Delete umtprd.conf from /etc
        umtprd_conf = Path("/etc/umtprd/umtprd.conf")
        umtprd_conf.unlink(missing_ok=True)
        if umtprd_conf.parent.exists():
            umtprd_conf.parent.rmdir()


    # Deploy umtprd.conf to the correct location
    @staticmethod
    def deploy_umtprd_conf():
        input_file = Path(decky_plugin.DECKY_PLUGIN_SETTINGS_DIR, "umtprd.conf")
        output_file = Path("/etc/umtprd/umtprd.conf")

        # Create the folder if it doesn't exist
        if not output_file.parent.exists():
            output_file.parent.mkdir()

        # Copy the file
        copy_template(input_file, output_file)

    # Add folder to umtprd
    @staticmethod
    def umtprd_add_folder(folder: Path, name: str) -> bool:
        # Check if the folder exists
        if not folder.exists():
            return False

        # The command to add the folder
        command: list[str] = [
            PLUGIN_BIN_DIR + "/umtprd",
            "-cmd:addstorage:" + str(folder) + ' "' + name + '"' + " rw",
        ]

        # Run the command
        return subprocess.run(command, check=False).returncode == 0

    # Add SD card folders
    @staticmethod
    def add_sdcard_folders():
        for folder in Path("/run/media").iterdir():
            if folder.is_mount():
                _ = MTP.umtprd_add_folder(folder, folder.name)


class Plugin:
    # Services to enable
    services: list[str] = [
        "gadget-bind.service",
        "gadget-init.service",
        "gadget-start.service",
    ]

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

        # Only use the bind service if the interface isn't bound to the correct driver
        if not Path("/sys/bus/pci/drivers/xhci_hcd/0000:04:00.3").is_file():
            self.services.remove("gadget-bind.service")

        _ = await Plugin.enable(self)
        _ = MTP.enable()

    # Function called first during the unload process,
    # utilize this to handle your plugin being removed
    async def _unload(self):
        # Stop MTP
        _ = await Plugin.stop_gadget(self)

        # Disable (remove) all systemd services
        _ = MTP.disable()
        _ = await Plugin.disable(self)

    # Enable services
    async def enable(self):
        _ = Systemctl.enable(self.services)

    # Disable services
    async def disable(self):
        _ = Systemctl.disable(self.services)

    # Check if umtprd is running
    async def is_running(self) -> bool:
        return is_running()

    # Check if Dual-Role Device is enabled in BIOS
    async def is_drd_enabled(self) -> bool:
        modules = subprocess.run("lsmod", capture_output=True, text=True, check=False).stdout
        return "dwc3" in modules

    # Start USB gadget
    async def start_gadget(self) -> bool:
        return Systemctl.start("usb-gadget.target")

    # Stop USB gadget
    async def stop_gadget(self) -> bool:
        return Systemctl.stop("usb-gadget.target")

    # Toggle USB Gadget
    async def toggle_gadget(self) -> bool:
        if not is_running():
            _ = await Plugin.start_gadget(self)
            MTP.add_sdcard_folders()
        else:
            _ = await Plugin.stop_gadget(self)
        return is_running()
