# bwpi - Bubblewrapped PI

`bwpi` runs the `pi` agent inside an isolated environment using
[bubblewrap](https://github.com/containers/bubblewrap).

The goal is to provide a lightweight sandbox for `pi` while keeping:

- network access;
- the current project directory writable;
- the user configuration `~/.pi`.

The system filesystem is mounted read-only to reduce the chance of
accidental modifications. By default, the project's `.git` directory is
also mounted read-only to prevent Git operations from modifying the
repository metadata.

Pass `--git-unlock` to mount the `.git` directory as writable, allowing
Pi to perform Git operations such as creating commits, switching
branches, or updating references.

## Requirements

### Linux

- Python 3.10 or newer
- bubblewrap (`bwrap`)
- Node.js and `pi` in `PATH`

### Windows

- Windows 10 version 2004, build 19041, or newer
- Python 3.10 or newer on Windows
- WSL2 with bubblewrap, Node.js, and `pi` installed in its default Linux
  distribution

Windows Node.js and Pi installations are not used. `bwpi` runs their WSL
versions and shares WSL's `~/.pi` configuration.

## Install on Windows

Windows commands below work in PowerShell or Command Prompt. Do not install
`bwpi` inside WSL.

### 1. Check WSL

In PowerShell or Command Prompt:

```console
wsl --status
```

If Windows cannot find `wsl`, or reports that WSL is not installed, open an
Administrator PowerShell or Command Prompt window and run:

```console
wsl --install
```

Restart Windows if requested. This command normally installs Ubuntu too.

### 2. Check Linux distribution

In PowerShell or Command Prompt:

```console
wsl --list --verbose
```

If no distribution appears, install Ubuntu:

```console
wsl --install --distribution Ubuntu
```

Launch Ubuntu once and create Linux username and password:

```console
wsl --distribution Ubuntu
```

The `VERSION` column from `wsl --list --verbose` must show `2`. If Ubuntu
uses WSL 1, convert it in PowerShell or Command Prompt:

```console
wsl --set-version Ubuntu 2
```

`bwpi` uses WSL's default distribution. Make Ubuntu default:

```console
wsl --set-default Ubuntu
```

If displayed distribution name differs from `Ubuntu`, use displayed name in
both commands.

### 3. Install WSL dependencies

Open Ubuntu, or run `wsl` from PowerShell or Command Prompt. Commands in
this section run **inside WSL**.

Install bubblewrap and curl:

```bash
sudo apt update
sudo apt install -y bubblewrap curl
```

Install [nvm](https://github.com/nvm-sh/nvm), then load it:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash
source ~/.bashrc
```

Install latest Node.js LTS release:

```bash
nvm install --lts
```

Install Pi:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Create configuration directory and verify dependencies:

```bash
mkdir -p ~/.pi
bwrap --version
node --version
pi --version
```

Return to Windows shell with `exit`.

### 4. Install bwpi on Windows

Commands in this section run in PowerShell or Command Prompt, not WSL.

#### With uv (recommended)

Install with `uv` (recommended). It creates an isolated environment and puts
`bwpi` on `PATH`:

```console
winget install --exact --id Astral.uv
git clone https://github.com/RobertoPorpora/Bubble-wrapped-Pi.git bwpi
cd bwpi
uv tool install .
```

For editable development install, use `uv tool install --editable .`.

#### With Python + Pip

Without `uv`, install with Python and pip instead:

Check Windows Python and Git first:

```console
py --version
git --version
```

If either command is missing, install it with `winget`, then reopen terminal:

```console
winget install --exact --id Python.Python.3.12
winget install --exact --id Git.Git
```


```console
git clone https://github.com/RobertoPorpora/Bubble-wrapped-Pi.git bwpi
cd bwpi
py -m pip install .
```

For editable development install, use `py -m pip install -e .` instead.

Verify from project to sandbox:

```console
cd path\to\your-project
bwpi --version
```

## Install on Linux

Install Python 3.10 or newer, bubblewrap, curl, and Git with distribution's
package manager. For Debian or Ubuntu:

```bash
sudo apt update
sudo apt install -y bubblewrap curl git python3 python3-pip
```

Install nvm, Node.js LTS, and Pi as current user:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash
source ~/.bashrc
nvm install --lts
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
mkdir -p ~/.pi
```

Install `uv` (recommended), then clone and install `bwpi`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
git clone https://github.com/RobertoPorpora/Bubble-wrapped-Pi.git bwpi
cd bwpi
uv tool install .
```

For editable development install, use `uv tool install --editable .`.

Without `uv`, install with Python and pip instead:

```bash
git clone https://github.com/RobertoPorpora/Bubble-wrapped-Pi.git bwpi
cd bwpi
python3 -m pip install .
```

Some distributions block system-wide `pip` installs. In that case, use a
virtual environment or `pipx`. For editable development install, use
`python3 -m pip install -e .` instead.

---

## Usage

Enter the project directory:

```bash
cd my-project
```

Start Pi:

```bash
bwpi
```

The command will run inside the bubblewrap sandbox.

To allow Pi to perform Git operations, run:

```bash
bwpi --git-unlock
```

When this option is specified, the project's .git directory is mounted
read-write. Without it, .git remains read-only while the rest of the
project directory is still writable.

---

## What gets isolated

`bwpi` uses bubblewrap with:

### Linux namespaces

* isolated PID namespace
* isolated mount namespace
* isolated IPC namespace
* isolated UTS namespace
* isolated user namespace

### Filesystem

The main filesystem is mounted:

```
/
```

read-only.

Writable locations:

```
current directory
~/.pi
/tmp
```

The current project directory is mounted back as writable so Pi can
modify project files.

By default, the project's `.git` directory remains mounted read-only,
preventing Git metadata from being modified.

Passing `--git-unlock` mounts `.git` as read-write,
enabling Pi to perform Git operations.

### Network

The network is kept available:

```
--share-net
```

so Pi can continue to access online services.

---

## Environment variables

`bwpi` preserves the required environment for running Pi.

Inside the sandbox:

* `PATH` is configured so Node.js installed through `nvm` is available;
* Pi configuration is shared;
* `HOME` points to the user home directory.

The sandbox does not use the Windows Node.js installation.

---

## Debug

To inspect the generated bubblewrap command:

temporarily add:

```python
print(" ".join(cmd))
```

before:

```python
subprocess.call(cmd)
```

in `cli.py`.

---

## Limitations

This is not a full container.

Bubblewrap provides isolation through Linux namespaces,
but the level of protection depends on the kernel configuration
and the user's permissions.

On Windows, the isolation boundary is provided by WSL2 plus
bubblewrap. WSL interoperability currently lets sandboxed processes launch
Windows executables outside bubblewrap restrictions. Do not treat Windows
mode as strong containment until WSL interoperability is disabled.

## To do

- Disable WSL interoperability
- Make `.git` directories in subfolders read-only
