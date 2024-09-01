from pathlib import Path
import subprocess
import sys

import decky_plugin

# Append py_modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent / "py_modules"))

from lib import utils
from lib import systemctl
from lib import mtp


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
        for config in utils.CONFIGS:
            input_file = Path(utils.PLUGIN_CONFIGS_DIR, config)
            output_file = Path(decky_plugin.DECKY_PLUGIN_SETTINGS_DIR, config)

            if not output_file.exists():
                utils.copy_template(input_file, output_file)

        # Copy services to correct directory
        for service in utils.SERVICES:
            input_file = Path(utils.PLUGIN_SERVICES_DIR, service)
            output_file = Path(decky_plugin.DECKY_PLUGIN_RUNTIME_DIR, service)

            # Define substitutions
            substitutions: dict[str, str] = {
                "bindir": utils.PLUGIN_BIN_DIR,
                "scriptsdir": utils.PLUGIN_SCRIPTS_DIR,
                "envfile": decky_plugin.DECKY_PLUGIN_SETTINGS_DIR + "/gadget",
            }

            # Replace templates and copy file
            utils.copy_template(input_file, output_file, substitutions)

        # Only use the bind service if the interface isn't bound to the correct driver
        if not Path("/sys/bus/pci/drivers/xhci_hcd/0000:04:00.3").is_file():
            self.services.remove("gadget-bind.service")

        Plugin.enable(self)
        mtp.enable()

    # Function called first during the unload process,
    # utilize this to handle your plugin being removed
    async def _unload(self):
        # Stop MTP
        _ = await Plugin.stop_gadget(self)

        # Disable (remove) all systemd services
        mtp.disable()
        Plugin.disable(self)

    # Enable services
    def enable(self):
        _ = systemctl.enable(self.services)

    # Disable services
    def disable(self):
        _ = systemctl.disable(self.services)

    # Check if umtprd is running
    async def is_running(self) -> bool:
        return systemctl.status("umtprd")

    # Check if Dual-Role Device is enabled in BIOS
    async def is_drd_enabled(self) -> bool:
        modules = subprocess.run("lsmod", capture_output=True, text=True, check=False).stdout
        return "dwc3" in modules

    # Start USB gadget
    async def start_gadget(self) -> bool:
        return systemctl.start("usb-gadget.target")

    # Stop USB gadget
    async def stop_gadget(self) -> bool:
        return systemctl.stop("usb-gadget.target")

    # Toggle USB Gadget
    async def toggle_gadget(self) -> bool:
        if not await Plugin.is_running(self):
            _ = await Plugin.start_gadget(self)
            mtp.add_sdcard_folders()
        else:
            _ = await Plugin.stop_gadget(self)
        return await Plugin.is_running(self)
