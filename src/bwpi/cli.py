import os
import shutil
import subprocess
import sys
from pathlib import Path


BWRAP_ARGS = [
    "--unshare-all",
    "--share-net",
    "--new-session",
    "--die-with-parent",

    "--ro-bind", "/", "/",

    "--proc", "/proc",
    "--dev", "/dev",
    "--tmpfs", "/tmp",
]


def require_command(name: str):
    if shutil.which(name) is None:
        raise RuntimeError(f"command '{name}' not found")


def run_command(cmd, **kwargs):
    return subprocess.check_output(
        cmd,
        text=True,
        **kwargs,
    ).strip()


def wsl_exec(wsl: str, command: str):
    return run_command(
        [
            wsl,
            "bash",
            "-ic",
            command,
        ]
    )


def add_pi_config(cmd, pi_config: str):
    if Path(pi_config).exists():
        cmd.extend([
            "--bind",
            pi_config,
            pi_config,
        ])


def build_bwrap_command(
    cwd: str,
    pi_path: str,
    pi_config: str | None = None,
    path: str | None = None,
):
    cmd = [
        "bwrap",
        *BWRAP_ARGS,
    ]

    if path:
        cmd.extend([
            "--setenv",
            "PATH",
            path,
        ])

    cmd.extend([
        "--bind",
        cwd,
        cwd,

        "--chdir",
        cwd,
    ])

    if pi_config:
        add_pi_config(cmd, pi_config)

    cmd.append(pi_path)

    cmd.extend(sys.argv[1:])

    return cmd


def run_pi_linux():
    require_command("bwrap")
    require_command("pi")

    cwd = str(Path.cwd())
    home = Path.home()

    cmd = build_bwrap_command(
        cwd=cwd,
        pi_path="pi",
        pi_config=str(home / ".pi"),
    )

    env = os.environ.copy()
    env["HOME"] = str(home)

    return subprocess.call(
        cmd,
        env=env,
    )


def windows_path_to_wsl(path: Path):
    drive = path.drive.rstrip(":").lower()
    rest = str(path)[2:].replace("\\", "/")

    return f"/mnt/{drive}{rest}"


def get_wsl_environment(wsl: str):
    pi_path = wsl_exec(
        wsl,
        "command -v pi",
    )

    if not pi_path:
        raise RuntimeError(
            "Cannot find pi inside WSL"
        )

    node_path = wsl_exec(
        wsl,
        "command -v node",
    )

    if not node_path:
        raise RuntimeError(
            "Cannot find node inside WSL"
        )

    node_bin = node_path.rsplit("/", 1)[0]

    path = wsl_exec(
        wsl,
        'printf "%s" "$PATH"',
    )

    if node_bin not in path.split(":"):
        path = f"{node_bin}:{path}"

    home = wsl_exec(
        wsl,
        'printf "%s" "$HOME"',
    )

    return {
        "pi": pi_path,
        "home": home,
        "path": path,
    }


def run_pi_windows():
    wsl = shutil.which("wsl")

    if wsl is None:
        raise RuntimeError(
            "WSL not found"
        )

    env = get_wsl_environment(wsl)

    cwd = windows_path_to_wsl(
        Path.cwd()
    )

    pi_config = f"{env['home']}/.pi"

    cmd = [
        wsl,
        "--cd",
        cwd,
        "-e",
        *build_bwrap_command(
            cwd=cwd,
            pi_path=env["pi"],
            pi_config=pi_config,
            path=env["path"],
        ),
    ]

    return subprocess.call(cmd)


def run_pi():
    if sys.platform == "win32":
        return run_pi_windows()

    return run_pi_linux()


def main():
    sys.exit(run_pi())


if __name__ == "__main__":
    main()