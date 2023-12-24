
# Developer Setup



## Installing Poetry
To install Poetry, run

```sh
pipx install poetry
```

Upgrade Poetry with `pipx upgrade poetry`.

Uninstall Poetry with `pipx uninstall poetry`.  

## Installing Pipx

To install `pipx` on Ubuntu, determine your version of Ubuntu with

```sh
lsb_release -a
```

For Ubuntu >23.04, install `pipx` with

```sh
sudo apt update
sudo apt install pipx
pipx ensurepath
```

For Ubuntu 22.04, install `pipx` with

```sh

```sh
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Upgrade pipx with `python3 -m pip install --user --upgrade pipx`.

