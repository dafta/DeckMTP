import os
import subprocess

import sys

# append py_modules to PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/py_modules")

import logging

logging.basicConfig(filename="/tmp/template.log",
                    format='[Template] %(asctime)s %(levelname)s %(message)s',
                    filemode='w+',
                    force=True)
logger=logging.getLogger()
logger.setLevel(logging.DEBUG) # can be changed to logging.DEBUG for debugging issues

# Return umtprd pid if running, or 0 otherwise
def get_umtprd_pid() -> int:
    pid = ""
    try:
        with subprocess.Popen(["pgrep", "--full", "--oldest", "umtprd"], stdout=subprocess.PIPE) as p:
            assert p.stdout is not None
            pid = p.stdout.read().strip()
            logger.info(pid)
    except:
        return 0
    if not pid:
        return 0
    return int(pid)

class Plugin:
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        logger.info("Hello World!")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        logger.info("Goodbye World!")
        pass

    # Check if umtprd is running
    async def is_running(self) -> bool:
        pid = get_umtprd_pid()
        if pid != 0:
            return True
        else:
            return False
