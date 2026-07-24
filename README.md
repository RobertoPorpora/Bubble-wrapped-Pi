# bwpi - Bubblewrapped PI

`bwpi` runs the `pi` agent inside an isolated environment using
[bubblewrap](https://github.com/containers/bubblewrap).

The goal is to provide a lightweight sandbox for `pi` while keeping:

- network access;
- the current project directory writable;
- the user configuration `~/.pi`.

The system filesystem is mounted read-only to reduce the chance of
accidental modifications.

## Requirements

### Linux

- Python >= 3.10
- bubblewrap (`bwrap`)
- `pi` installed and available in PATH

### Windows

On Windows, `bwpi` uses **WSL2** because bubblewrap requires a Linux
environment.

The expected setup is:

```
Windows
└── WSL2
    ├── bubblewrap
    └── Node.js
        └── pi
````

`bwpi` automatically:

- converts the Windows working directory into a WSL path;
- finds `pi` inside WSL;
- finds the Node.js installation used by `pi`;
- configures the sandbox PATH;
- shares the WSL `~/.pi` configuration.

The Windows installation of Node.js or Pi is not used.

---

## Installing WSL2 on Windows

Open PowerShell as Administrator:

```powershell
wsl --install
````

Restart Windows if requested.

After reboot, open the installed Linux distribution
(Ubuntu is recommended) and create your Linux user.

Verify WSL2:

```powershell
wsl --status
```

---

## Installing dependencies inside WSL

Open your WSL terminal.

Update packages:

```bash
sudo apt update
sudo apt upgrade -y
```

### Install bubblewrap

Debian/Ubuntu:

```bash
sudo apt install bubblewrap
```

Fedora:

```bash
sudo dnf install bubblewrap
```

Arch:

```bash
sudo pacman -S bubblewrap
```

Verify:

```bash
bwrap --version
```

---

## Install Node.js inside WSL

The recommended method is `nvm`.

Install nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
```

Reload your shell:

```bash
source ~/.bashrc
```

Install Node.js:

```bash
nvm install node
```

Verify:

```bash
node --version
```

---

## Install Pi inside WSL

Install Pi using npm:

```bash
npm install -g pi
```

Verify:

```bash
pi --version
```

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd bwpi
```

Install the package:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

After installation:

```bash
bwpi
```

will be available.

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
bubblewrap.
