BKOS is an extensible explanatory dialogue system informed by theories of human argumentation, rhetoric and dialogue.

The system's dialogue capabilities are described in the following paper:

Berman, A. and S. Larsson (2025, in prep). Assessing Conversational Capabilities of Explanatory AI Interfaces. In _Proceedings of the International Conference on Artificial Intelligence in HCI, Held as Part of HCI International 2025.

An earlier version of the central concepts and ideas in BKOS is described in the following papers:

Berman, A. (2024). [Argumentative Dialogue As Basis For Human-AI Collaboration](https://ceur-ws.org/Vol-3825/short3-2.pdf). In _Proceedings of the Communication in Human-AI Interaction Workshop (CHAI-2024)_.

# Requirements
BKOS has been tested with Python >= 3.8.

# Installation
It is recommended to install and use BKOS inside a virtual environment, e.g. with virtualenv or conda. Then, install BKOS with

```commandline
pip install .
```

# Domains
The repo contains two example domains (use cases): `hello_world` (minimal loan application scenario with pre-determined prediction and explanation) and `music_personality` (more elaborate scenario involving prediction of personality from music preferences).

# Automated testing
The domains contain coverage tests which documented supported dialogue behaviours. The tests can be run as follows:

```commandline
pytest .
```
# Demo
This repo contains a very simple "hello world" demo which can be tested in the command line by running

```commandline
bkos interact
```
