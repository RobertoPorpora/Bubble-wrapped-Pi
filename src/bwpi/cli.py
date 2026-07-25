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

def parse_wrapper_args():
    git_unlock = False
    forwarded = []

    for arg in sys.argv[1:]:
        if arg == "--git-unlock":
            git_unlock = True
        else:
            forwarded.append(arg)

    return git_unlock, forwarded

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

def wsl_path_exists(wsl: str, path: str) -> bool:
    return (
        subprocess.call(
            [
                wsl,
                "bash",
                "-lc",
                f'test -e "{path}"',
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        == 0
    )

def add_pi_config(
    cmd,
    pi_config: str,
    wsl: str | None = None,
):
    if wsl is None:
        exists = Path(pi_config).exists()
    else:
        exists = wsl_path_exists(wsl, pi_config)

    if exists:
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
    wsl: str | None = None,
    git_unlock: bool = False,
    pi_args: list[str] | None = None,
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
    ])

    if not git_unlock:
        host_git = Path.cwd() / ".git"
        if host_git.is_dir():
            cmd.extend([
                "--ro-bind",
                f"{cwd}/.git",
                f"{cwd}/.git",
            ])


    cmd.extend([
        "--chdir",
        cwd,
    ])

    if pi_config:
        add_pi_config(cmd, pi_config, wsl)

    cmd.append(pi_path)

    if pi_args:
        cmd.extend(pi_args)
    
    return cmd


def run_pi_linux():
    require_command("bwrap")
    require_command("pi")

    cwd = str(Path.cwd())
    home = Path.home()

    git_unlock, pi_args = parse_wrapper_args()

    cmd = build_bwrap_command(
        cwd=cwd,
        pi_path="pi",
        pi_config=str(home / ".pi"),
        git_unlock=git_unlock,
        pi_args=pi_args,
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

    git_unlock, pi_args = parse_wrapper_args()

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
            wsl=wsl,
            git_unlock=git_unlock,
            pi_args=pi_args,
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