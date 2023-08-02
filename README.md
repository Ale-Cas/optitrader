<div align="center">

<h1> Optitrader </h1>

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://optitrader.streamlit.app/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.24.0-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io)

![Build](https://github.com/Ale-Cas/optitrader/actions/workflows/test.yml/badge.svg)
[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![codecov](https://codecov.io/github/Ale-Cas/optitrader/branch/master/graph/badge.svg?token=F0COJXH0IJ)](https://codecov.io/github/Ale-Cas/optitrader)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Ale-Cas/optitrader)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Pydantic v1](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/5697b1e4c4a9790ece607654e6c02a160620c7e1/docs/badge/v1.json)](https://pydantic.dev)
[![jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter)](https://jupyterlab.readthedocs.io/en/stable)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.63.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
</div>

Optitrader is an open-source Python package designed for portfolio optimization, quantitative finance, and algorithmic trading. It empowers users with a wide array of tools to effortlessly construct personalized portfolios, thoroughly analyze optimization outcomes, and seamlessly execute trades using [Alpaca's Trading API](https://alpaca.markets/docs/trading/).

Accessible through an intuitive web-based [Streamlit](https://streamlit.io/) dashboard hosted at https://optitrader.streamlit.app, Optitrader enables users to interact with its rich features and harness the potential of portfolio optimization and algorithmic trade execution.

## Using

_Python package_: to add and install this package as a dependency of your project, run `poetry add optitrader`.

_Python CLI_: to view this app's CLI commands once it's installed, run `optitrader --help`.

_Rest API_: to serve this application as a REST API, run `docker compose up app` and open [localhost:8080](http://localhost:8080) in your browser to see the documentation. Within the Dev Container, this is equivalent to running `poe api`.

_Streamlit Dashboard_: to use this application from a Streamlit dashboard, run `optitrader dashboard`. This is equivalent to running `poe app` and open [localhost:8000](http://localhost:8000) in your browser.

## Example

Once the package has been installed you can use it as follows:
```python
from optitrader import Optitrader
from optitrader.optimization.objectives import CVaRObjectiveFunction
from optitrader.enums import UniverseName

optimal_ptf = Optitrader(
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
and you can use the available methods of the [Portfolio class](src/optitrader/portfolio.py), such as `pie_plot`:
```python
optimal_ptf.pie_plot()
```
![pieplot](https://github.com/Ale-Cas/optitrader/assets/64859146/3728507d-8f5d-472e-8131-129e2d54c211)



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
1. ⭐️ _Dev Container (with container volume)_: click on [Open in Dev Containers](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Ale-Cas/optitrader) to clone this repository in a container volume and create a Dev Container with VS Code.
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
optitrader is built by keeping in mind the availability of other great open-source repositories, such as:

- [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib)
- [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt)
