import os
import subprocess
import sys

import decky_plugin

# append py_modules to PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/py_modules")

PLUGIN_BIN_DIR: str = decky_plugin.DECKY_PLUGIN_DIR + "/bin"


# Create a subprocess environment with an empty LD_LIBRARY_PATH
env: dict[str, str] = os.environ.copy()
del env["LD_LIBRARY_PATH"]


# Return umtprd pid if running, or 0 otherwise
def get_umtprd_pid() -> int:
    pid = ""
    try:
        with subprocess.Popen(
            ["pgrep", "--full", "--oldest", "umtprd"], stdout=subprocess.PIPE, env=env
        ) as p:
            assert p.stdout is not None
            pid = p.stdout.read().strip()
    except Exception:
        return 0
    if not pid:
        return 0
    return int(pid)


# Check if umtprd is running
def is_running() -> bool:
    pid = get_umtprd_pid()
    if pid != 0:
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
            with subprocess.Popen(
                "lsmod | grep dwc3", shell=True, stdout=subprocess.PIPE, env=env
            ) as p:
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
            _ = subprocess.run("./start.sh", cwd=PLUGIN_BIN_DIR, shell=True, env=env)
        else:
            _ = subprocess.run("./stop.sh", cwd=PLUGIN_BIN_DIR, shell=True, env=env)
        return is_running()

    # Stop MTP
    async def stop_mtp(self):
        if not is_running():
            return
        _ = subprocess.run("./stop.sh", cwd=PLUGIN_BIN_DIR, shell=True, env=env)
