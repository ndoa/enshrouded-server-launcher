# ---------------- #
# ---- Config ---- #
# ---------------- #

# Filename and path of the dedicated server executable:
EXECUTABLE_NAME = "enshrouded_server.exe"
EXECUTABLE_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\EnshroudedServer"

# Maximum amount of time to wait for the server to correctly start before exiting and retrying.
# This value is in seconds.
MAX_START_TIMEOUT = 10


# Enable colored terminal output using ANSI escape codes
# If you see output like "\033[95m" in your output, your console doesn't support this feature.
ENABLE_ANSI_COLOR = True

# ----------------------------------------------------------------------------- #
# ---- Don't modify anything below this unless you know what you're doing. ---- #
# ----------------------------------------------------------------------------- #

import os
import subprocess
import signal
import sys
import time

LAUNCHER_PREFIX = "[ndoa server launcher]: "

if ENABLE_ANSI_COLOR:
    class bcolors:
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKCYAN = "\033[96m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
else:
    class bcolors:
        HEADER = ""
        OKBLUE = ""
        OKCYAN = ""
        OKGREEN = ""
        WARNING = ""
        FAIL = ""
        ENDC = ""
        BOLD = ""
        UNDERLINE = ""


def signal_handler(sig, frame):
    print("Ctrl+C pressed - exiting.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def start_server_ensure_online():
    while True:
        start_time = time.time()

        current_process = subprocess.Popen(
            [os.path.join(EXECUTABLE_PATH, EXECUTABLE_NAME)],
            cwd=EXECUTABLE_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Set the stdout/stderr handles to non-blocking so that
        # we can constantly poll them for data and stream out.
        os.set_blocking(current_process.stdout.fileno(), False)
        os.set_blocking(current_process.stderr.fileno(), False)

        # Stream stdout/stderr until we see the "good" messages (connected to steam)
        # or exit after the configured timeout is reached.
        start_success = False
        while (time.time() - start_time < MAX_START_TIMEOUT) or start_success:
            stdout_line = current_process.stdout.readline()
            if len(stdout_line) > 0:
                stdout_line = stdout_line.decode("utf-8")
                print(f"{bcolors.OKBLUE}{stdout_line}{bcolors.ENDC}", end="")

                # Server started successfully, keep the std[err|out] loop piping.
                if "[online] Server connected to Steam successfully" in stdout_line:
                    start_success = True
                    print(
                        f"{bcolors.OKGREEN}{LAUNCHER_PREFIX}Enshrouded server started successfully - 'Game Creation Failed' bug will not happen on join. {bcolors.ENDC}"
                    )

            stderr_line = current_process.stderr.readline()
            if len(stderr_line) > 0:
                stderr_line = stderr_line.decode("utf-8")
                print(f"{bcolors.WARNING}{stderr_line}{bcolors.ENDC}", end="")

        if not start_success:
            print(
                f"{bcolors.FAIL}{LAUNCHER_PREFIX}Enshrouded server was unable to successfully start after {MAX_START_TIMEOUT} seconds. Retrying!{bcolors.ENDC}"
            )

        # Terminate and give a couple of seconds for the Steam API to properly clean up
        # before the process starts again and immediately tries to connect to steam/register callbacks.
        current_process.terminate()
        time.sleep(3)


if __name__ == "__main__":
    start_server_ensure_online()
