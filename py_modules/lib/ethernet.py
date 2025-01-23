from pathlib import Path
import subprocess

import decky

from . import utils
from . import systemctl

# Services to enable
networks: list[str] = ["usb0.network"]

# Services to enable
services: list[str] = ["usbgadget-func-ecm.service"]


def enable():
    # Deploy networks to the correct location
    deploy_networks()

    # Start iptables and systemd-networkd
    _ = systemctl.start("iptables.service", "systemd-networkd.service")

    # Enable NAT
    command: list[str] = ["iptables", "-t", "-nat", "-A", "-j", "MASQUERADE"]
    _ = subprocess.run(command, check=False)

    _ = systemctl.enable(services)


def disable():
    _ = systemctl.disable(services)

    # Delete networks from /etc/systemd/networkd
    for network in networks:
        network = Path("/etc/systemd/network", network)
        network.unlink(missing_ok=True)

    # Disable NAT
    command: list[str] = ["iptables", "-t", "-nat", "-D", "-j", "MASQUERADE"]
    _ = subprocess.run(command, check=False)

    # Stop systemd-networkd
    _ = systemctl.stop("systemd-networkd")


def is_enabled():
    for service in services:
        if not systemctl.is_enabled(service):
            return False

    return True


def toggle():
    if is_enabled():
        disable()
    else:
        enable()


# Deploy networks to the correct location
def deploy_networks():
    for network in networks:
        input_file = Path(decky.DECKY_PLUGIN_RUNTIME_DIR, network)
        output_file = Path("/etc/systemd/network", network)

        utils.copy_template(input_file, output_file)
