from pathlib import Path
import subprocess
import sys

# Append py_modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent / "py_modules"))

from lib import utils
from lib import systemctl

from lib.mtp import Mtp
from lib.ethernet import Ethernet


class Plugin:
    # Services to enable
    services: list[str] = [
        "gadget-bind.service",
        "gadget-init.service",
        "gadget-start.service",
    ]

    # MTP gadget plugin
    mtp: Mtp

    # Ethernet gadget plugin
    ethernet: Ethernet

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        # Install plugin files
        utils.install()

        # Only use the bind service if the interface isn't bound to the correct driver
        if not Path("/sys/bus/pci/drivers/xhci_hcd/0000:04:00.3").is_file():
            self.services.remove("gadget-bind.service")

        # Init plugin
        Plugin.enable(self)

        # Init gadget plugins
        Plugin.mtp = Mtp()
        Plugin.ethernet = Ethernet()

    # Function called first during the unload process,
    # utilize this to handle your plugin being removed
    async def _unload(self):
        # Stop USB gadget
        _ = await Plugin.stop_usb(self)

        # Disable (remove) all systemd services
        Plugin.disable(self)

    # Function called when the plugin is uninstalled
    async def _uninstall(self):
        # Stop USB gadget
        _ = await Plugin.stop_usb(self)

        # Disable (remove) all systemd services
        Plugin.disable(self)

    # Enable services
    def enable(self):
        _ = systemctl.enable(self.services)

    # Disable services
    def disable(self):
        Plugin.mtp.disable()
        Plugin.ethernet.disable()
        _ = systemctl.disable(self.services)

    # Check if Dual-Role Device is enabled in BIOS
    async def is_drd_enabled(self) -> bool:
        modules = subprocess.run(
            "lsmod", capture_output=True, text=True, check=False
        ).stdout
        return "dwc3" in modules

    # Check if USB function is enabled
    async def is_function_enabled(self, function: str) -> bool:
        match function:
            case "mtp":
                return Plugin.mtp.is_enabled()
            case "ethernet":
                return Plugin.ethernet.is_enabled()
            case _:
                return False

    # Toggle USB function
    async def toggle_function(self, function: str):
        match function:
            case "mtp":
                Plugin.mtp.toggle()
            case "ethernet":
                Plugin.ethernet.toggle()
            case _:
                pass

    # Check if USB gadget is running
    async def is_running(self) -> bool:
        return systemctl.is_active("gadget-start.service")

    # Start USB gadget
    async def start_usb(self) -> bool:
        return systemctl.start("usb-gadget.target")

    # Stop USB gadget
    async def stop_usb(self) -> bool:
        return systemctl.stop("usb-gadget.target")

    # Toggle USB gadget
    async def toggle_usb(self):
        if not await Plugin.is_running(self):
            _ = await Plugin.start_usb(self)
            if Plugin.mtp.is_enabled():
                Plugin.mtp.add_sdcard_folders()
        else:
            _ = await Plugin.stop_usb(self)
