from pathlib import Path
import subprocess

from settings import SettingsManager
import decky

from . import utils
from . import systemctl


class Ethernet:
    # Services to enable
    networks: list[str] = ["usb0.network"]

    # Services to enable
    services: list[str] = ["usbgadget-func-ecm.service"]

    # Ethernet settings
    settings: SettingsManager

    def __init__(self):
        # Init settings
        Ethernet.settings = SettingsManager(
            name="ethernet", settings_directory=decky.DECKY_PLUGIN_SETTINGS_DIR
        )
        Ethernet.settings.read()

        if Ethernet.settings.getSetting("enabled", False):
            Ethernet.enable(self)

    def enable(self):
        # Deploy networks to the correct location
        Ethernet.deploy_networks(self)

        # Start iptables and systemd-networkd
        _ = systemctl.start("iptables.service", "systemd-networkd.service")

        # Enable NAT
        command: list[str] = ["iptables", "-t", "-nat", "-A", "-j", "MASQUERADE"]
        _ = subprocess.run(command, check=False)

        # Enable services
        _ = systemctl.enable(self.services)

    def disable(self):
        # Disable services
        _ = systemctl.disable(self.services)

        # Delete networks from /etc/systemd/networkd
        for network in self.networks:
            network = Path("/etc/systemd/network", network)
            network.unlink(missing_ok=True)

        # Disable NAT
        command: list[str] = ["iptables", "-t", "-nat", "-D", "-j", "MASQUERADE"]
        _ = subprocess.run(command, check=False)

        # Stop systemd-networkd
        _ = systemctl.stop("systemd-networkd")

    def is_enabled(self) -> bool:
        for service in self.services:
            if not systemctl.is_enabled(service):
                return False

        return True

    def toggle(self):
        if Ethernet.is_enabled(self):
            Ethernet.settings.setSetting("enabled", False)
            Ethernet.disable(self)
        else:
            Ethernet.settings.setSetting("enabled", True)
            Ethernet.enable(self)

    # Deploy networks to the correct location
    def deploy_networks(self):
        for network in self.networks:
            input_file = Path(decky.DECKY_PLUGIN_RUNTIME_DIR, network)
            output_file = Path("/etc/systemd/network", network)

            utils.copy_template(input_file, output_file)
