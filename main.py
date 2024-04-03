import os
import subprocess
import sys

import decky_plugin


# append py_modules to PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/py_modules")

PLUGIN_BIN_DIR: str = decky_plugin.DECKY_PLUGIN_DIR + "/bin"


# Helper for systemctl commands
def systemctl(*args: str) -> int:
    command: list[str] = [ 'systemctl' ]
    command.extend(args)
    return subprocess.run(command).returncode


# Check if umtprd is running
def is_running() -> bool:
    if systemctl('status', 'umtprd') == 0:
        return True
    else:
        return False


class Plugin:
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        pass

    # Function called first during the unload process,
    # utilize this to handle your plugin being removed
    async def _unload(self):
        await self.stop_mtp()
        pass

    # Check if umtprd is running
    async def is_running(self) -> bool:
        return is_running()

    # Check if Dual-Role Device is enabled in BIOS
    async def is_drd_enabled(self) -> bool:
        try:
            with subprocess.Popen("lsmod | grep dwc3", shell=True, stdout=subprocess.PIPE) as p:
                assert p.stdout is not None
                result = p.stdout.read().strip()
        except Exception:
            return False
        if not result:
            return False
        else:
            return True

    # Toggle MTP
    async def toggle_mtp(self) -> bool:
        if not is_running():
            _ = subprocess.run("./start.sh", cwd=PLUGIN_BIN_DIR, shell=True)
        else:
            _ = subprocess.run("./stop.sh", cwd=PLUGIN_BIN_DIR, shell=True)
        return is_running()

    # Stop MTP
    async def stop_mtp(self):
        if not is_running():
            return
        _ = subprocess.run("./stop.sh", cwd=PLUGIN_BIN_DIR, shell=True)
