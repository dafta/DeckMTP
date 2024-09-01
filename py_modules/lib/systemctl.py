import subprocess

import decky

# Helper for systemctl commands


# Systemctl status
def status(service: str) -> bool:
    command: list[str] = ["systemctl", "status"]
    command.append(service)
    return subprocess.run(command, check=False).returncode == 0


# Systemctl enable
def enable(services: list[str]) -> bool:
    command: list[str] = ["systemctl", "enable"]

    for service in services:
        command.append(decky.DECKY_PLUGIN_RUNTIME_DIR + "/" + service)

    return subprocess.run(command, check=False).returncode == 0


# Systemctl disable
def disable(services: list[str]) -> bool:
    command: list[str] = ["systemctl", "disable"]
    command.extend(services)
    return subprocess.run(command, check=False).returncode == 0


# Systemctl start
def start(*args: str) -> bool:
    command: list[str] = ["systemctl", "start"]
    command.extend(args)
    return subprocess.run(command, check=False).returncode == 0


# Systemctl stop
def stop(*args: str) -> bool:
    command: list[str] = ["systemctl", "stop"]
    command.extend(args)
    return subprocess.run(command, check=False).returncode == 0
