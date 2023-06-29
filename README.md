![Build](https://github.com/Ale-Cas/optifolio/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/github/Ale-Cas/optifolio/branch/master/graph/badge.svg?token=F0COJXH0IJ)](https://codecov.io/github/Ale-Cas/optifolio)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Ale-Cas/optifolio)

# Optifolio
![Optimal Portfolio](https://github.com/Ale-Cas/optifolio/assets/64859146/cccaf95c-4bb8-460c-81d9-a2f4fbc621fa)

## Description 

Optifolio is an open-source Python package for portfolio optimization and quantitative finance applications. 
It is meant to provide a comprehensive suite of tools to easily build a custom portfolio, analyze the optimization results and it also supports the trade execution by leveraging [Alpaca's Trading API](https://alpaca.markets/docs/trading/).

## Using

_Python package_: to add and install this package as a dependency of your project, run `poetry add optifolio`.

_Python CLI_: to view this app's CLI commands once it's installed, run `optifolio --help`.

_Rest API_: to serve this application as a REST API, run `docker compose up app` and open [localhost:8080](http://localhost:8080) in your browser to see the documentation. Within the Dev Container, this is equivalent to running `poe api`.

_Streamlit Dashboard_: to use this application from a Streamlit dashboard, run `optifolio dashboard`. This is equivalent to running `poe app` and open [localhost:8000](http://localhost:8000) in your browser.

## Example

Once the package has been installed you can use it as follows:
```python
from optifolio import Optifolio
from optifolio.optimization.objectives import CVaRObjectiveFunction
from optifolio.enums import UniverseName

optimal_ptf = Optifolio(
        objectives=[CVaRObjectiveFunction()],
        universe_name=UniverseName.POPULAR_STOCKS,
    ).solve()

# Optimal Portfolio:
Portfolio(
    weights={
        'AAPL': 0.18168,
        'BABA': 0.00369,
        'BRK.B': 0.15119,
        'META': 0.04067,
        'MSFT': 0.01936,
        'ORCL': 0.16028,
        'PFE': 0.00207,
        'TSLA': 0.01057,
        'V': 0.02516,
        'WMT': 0.40532
        }, 
    objective_values={
        'Conditional Value at Risk': 0.007560866163075728
        }
)
```

## Contributing

This project has been boostrapped using [this cookiecutter template](https://github.com/radix-ai/poetry-cookiecutter).

<details>
<summary>Prerequisites</summary>

<details>
<summary>1. Set up Git to use SSH</summary>

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:
    ```sh
    cat << EOF >> ~/.ssh/config
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
    EOF
    ```

</details>

<details>
<summary>2. Install Docker</summary>

1. [Install Docker Desktop](https://www.docker.com/get-started).
    - Enable _Use Docker Compose V2_ in Docker Desktop's preferences window.
    - _Linux only_:
        - [Configure Docker to use the BuildKit build system](https://docs.docker.com/build/buildkit/#getting-started). On macOS and Windows, BuildKit is enabled by default in Docker Desktop.
        - Export your user's user id and group id so that [files created in the Dev Container are owned by your user](https://github.com/moby/moby/issues/3206):
            ```sh
            cat << EOF >> ~/.bashrc
            export UID=$(id --user)
            export GID=$(id --group)
            EOF
            ```

</details>

<details>
<summary>3. Install VS Code or PyCharm</summary>

1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
2. _Optional:_ install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [configure PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use it.

</details>

</details>

<details open>
<summary>Development environments</summary>

The following development environments are supported:

1. ⭐️ _GitHub Codespaces_: click on _Code_ and select _Create codespace_ to start a Dev Container with [GitHub Codespaces](https://github.com/features/codespaces).
1. ⭐️ _Dev Container (with container volume)_: click on [Open in Dev Containers](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Ale-Cas/optifolio) to clone this repository in a container volume and create a Dev Container with VS Code.
1. _Dev Container_: clone this repository, open it with VS Code, and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Dev Containers: Reopen in Container_.
1. _PyCharm_: clone this repository, open it with PyCharm, and [configure Docker Compose as a remote interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote) with the `dev` service.
1. _Terminal_: clone this repository, open it with your terminal, and run `docker compose up --detach dev` to start a Dev Container in the background, and then run `docker compose exec dev zsh` to open a shell prompt in the Dev Container.

</details>

<details>
<summary>Developing</summary>

- This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
- Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
- Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`. Add `--group test` or `--group dev` to install a CI or development dependency, respectively.
- Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.
- Run `cz bump` to bump the package's version, update the `CHANGELOG.md`, and create a git tag.

</details>


## Similar projects 
Optifolio is built by keeping in mind the availability of other great open-source repositories, such as:

- [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib)
- [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt)
