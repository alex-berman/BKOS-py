BKOS is an extensible explanatory dialogue system informed by theories of human argumentation, rhetoric and dialogue.

The system's dialogue capabilities are described in the following paper:

Berman, A. and S. Larsson (2025, in prep). Assessing Conversational Capabilities of Explanatory AI Interfaces. In _Proceedings of the International Conference on Artificial Intelligence in HCI, Held as Part of HCI International 2025.

An earlier version of the central concepts and ideas in BKOS is described in the following papers:

Berman, A. (2024). [Argumentative Dialogue As Basis For Human-AI Collaboration](https://ceur-ws.org/Vol-3825/short3-2.pdf). In *Proceedings of the Communication in Human-AI Interaction Workshop (CHAI-2024)*.

The name BKOS, pronounced as "because", extends the notion of KoS (conversation oriented semantics; see J. Ginzburg, Semantics for Conversation, 2008).

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
# Demos
For a web-based demo, see the game [MindTone](https://dev.clasp.gu.se/mindtone/), revolving around estimating persons' personality based on their music preferences. A minimal version of MindTone can be tested in the command line by running

```commandline
bkos interact bkos.music_personality.config
```

Note that the minimal version only supports a single case, without any gaming elements.

This repo also contains a very simple "hello world" demo which can be tested in the command line by running

```commandline
bkos interact bkos.hello_world.config
```
