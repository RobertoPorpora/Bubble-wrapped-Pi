# bwpi - Bubblewrapped PI

`bwpi` runs the `pi` command inside an isolated environment using
[bubblewrap](https://github.com/containers/bubblewrap).

The goal is to provide a lightweight sandbox for `pi` while keeping:
- network access;
- the current project directory writable;
- the user configuration `~/.pi`;
- the current shell environment.

The system filesystem is mounted read-only to reduce the chance of
accidental modifications.

## Requirements

- Linux
- Python >= 3.10
- bubblewrap (`bwrap`)
- the `pi` command available in the PATH

Installing bubblewrap:

Debian/Ubuntu:

```bash
sudo apt install bubblewrap
````

Fedora:

```bash
sudo dnf install bubblewrap
```

Arch:

```bash
sudo pacman -S bubblewrap
```

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

To install it in development mode:

```bash
pip install -e .
```

After installation the following will be available:

```bash
bwpi
```

## Usage

Enter the project directory:

```bash
cd my-project
```

Start pi:

```bash
bwpi
```

The command will run inside the sandbox.

## What gets isolated

`bwpi` uses bubblewrap with:

### Linux namespaces

* isolated PID
* isolated mounts
* isolated IPC
* isolated UTS
* isolated user namespace

### Filesystem

The main filesystem is mounted:

```
/
```

read-only.

The following are writable:

```
current directory
~/.pi
/tmp
```

### Network

The network is kept via:

```
--share-net
```

so `pi` can continue to access online services.

## Environment variables

`bwpi` automatically inherits the shell environment:

* PATH
* API key
* proxy
* local configurations
* personal variables

The variable:

```
HOME
```

is automatically set to the home of the current user.

## Debug

To see the generated bubblewrap command:

temporarily edit `cli.py` adding:

```python
print(" ".join(cmd))
```

before running `subprocess.call`.

## Limitations

This is not a full container.

Bubblewrap provides isolation through Linux namespaces,
but the level of security depends on the kernel configuration
and the user's permissions.
