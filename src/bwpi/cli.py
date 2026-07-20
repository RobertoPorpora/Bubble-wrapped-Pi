import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_pi():
    cwd = Path.cwd()
    home = Path.home()
    pi_config = home / ".pi"

    if shutil.which("bwrap") is None:
        raise RuntimeError(
            "bubblewrap (bwrap) not found in PATH"
        )

    if not shutil.which("pi"):
        raise RuntimeError(
            "command 'pi' not found in PATH"
        )

    cmd = [
        "bwrap",

        # Namespace isolation:
        #
        # --unshare-all
        #   creates separate Linux namespaces:
        #   mount, PID, IPC, UTS, user and network
        #
        # --share-net
        #   keeps the host network.
        #   Without this pi would have no internet access.
        #
        # --new-session
        #   creates a new terminal session.
        #
        # --die-with-parent
        #   closes the sandbox when the parent process terminates.
        "--unshare-all",
        "--share-net",
        "--new-session",
        "--die-with-parent",

        # Filesystem:
        #
        # exposes the whole host filesystem read-only.
        # Writable directories are added afterwards
        # with --bind.
        "--ro-bind", "/", "/",

        # Virtual mounts needed by Linux programs.
        #
        # /proc:
        #   process information.
        #
        # /dev:
        #   system devices (tty, null, random...).
        #
        # /tmp:
        #   isolated temporary directory.
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/tmp",

        # Working directory:
        #
        # makes the current directory writable.
        "--bind", str(cwd), str(cwd),

        # Initial working directory
        "--chdir", str(cwd),
    ]

    # Pi user configuration.
    # Shared only if it exists, otherwise the command would fail.
    if pi_config.exists():
        cmd.extend(["--bind", str(pi_config), str(pi_config),])

    # Run Pi inside Bubblewrap
    cmd.append("pi")

    # Add any extra arguments passed via CLI
    cmd.extend(sys.argv[1:])

    # Keep the current environment.
    # Automatically passes PATH, API key, proxy, locale and other configurations.
    env = os.environ.copy()

    # HOME is normalized to avoid weird environment configurations
    env["HOME"] = str(home)

    result = subprocess.call(
        cmd,
        env=env,
    )

    sys.exit(result)


def main():
    run_pi()


if __name__ == "__main__":
    main()
