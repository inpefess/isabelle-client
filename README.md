[![PyPI
version](https://badge.fury.io/py/isabelle-client.svg)](https://badge.fury.io/py/isabelle-client)[![Anaconda
version](https://anaconda.org/conda-forge/isabelle-client/badges/version.svg)](https://anaconda.org/conda-forge/isabelle-client)[![CircleCI](https://circleci.com/gh/inpefess/isabelle-client.svg?style=svg)](https://circleci.com/gh/inpefess/isabelle-client)[![Documentation
Status](https://readthedocs.org/projects/isabelle-client/badge/?version=latest)](https://isabelle-client.readthedocs.io/en/latest/?badge=latest)[![codecov](https://codecov.io/gh/inpefess/isabelle-client/branch/master/graph/badge.svg)](https://codecov.io/gh/inpefess/isabelle-client)[![DOI](https://img.shields.io/badge/DOI-10.1007%2F978--3--031--16681--5__24-blue)](https://doi.org/10.1007/978-3-031-16681-5_24)

# Python client for Isabelle server

`isabelle-client` is a TCP client for
[Isabelle](https://isabelle.in.tum.de) server. For more information
about the server see Chapter 4 of [the Isabelle system
manual](https://dists.isabelle.cit.tum.de/dist/Isabelle2026/doc/system.pdf?token=Isabelle#page=54).

# How to Install

The best way to install this package is to use `pip`:

``` sh
pip install isabelle-client
```

Another option is to use Anaconda:

``` sh
conda install -c conda-forge isabelle-client 
```

One can also download and run the client together with Isabelle in a
Docker container:

``` sh
docker build -t isabelle-client https://github.com/inpefess/isabelle-client.git
docker run -d --rm -p 8888:8888 --name isabelle-client isabelle-client
```

And navigate to [example
page](http://localhost:8888/lab/tree/isabelle-client-examples/example.ipynb)
in your browser.

# How to use

``` python
from isabelle_client import get_isabelle_client, start_isabelle_server

# start Isabelle server
server_info, _ = start_isabelle_server()
# create a client object
isabelle = get_isabelle_client(server_info)
# start a new session
responses = isabelle.session_start()
session_id = responses[-1].response_body.session_id
# send a theory file from the current directory to the server
responses = isabelle.use_theories(
    theories=["Example"], master_dir=".", session_id=session_id
)
# shut the server down
isabelle.shutdown()
```

For more details, follow the [usage
example](https://isabelle-client.readthedocs.io/en/latest/example.html)
from documentation or a
[notebook](https://github.com/inpefess/isabelle-client/blob/master/examples/example.ipynb).

# High-level connector

You can also pass a theory file body (something you typically put
between `begin` and `end` keywords) to a high-level connector that will
generate a temporary file for you, send it to the Isabelle server and
get the result for you. For example, this snippet:

``` python
from isabelle_client.isabelle_connector import IsabelleConnector
from isabelle_client.isabelle_connector import IsabelleTheoryError

isabelle_connector = IsabelleConnector()
try:
    isabelle_connector.build_theory(
        r'lemma "\<forall> x. \<forall> y. x = y"' "\nby auto"
    )
    print("Theory is validated!")
except IsabelleTheoryError as error:
    print(error.args[0])
```

will produce something like:

``` 
: Failed to finish proof\<^here>:
: goal (1 subgoal):
:  1. \<And>x y. x = y
```

# More documentation

More documentation can be found
[here](https://isabelle-client.readthedocs.io/en/latest).

# Similar Software

There are Python clients to other interactive theorem provers, for
example:

- [for Lean](https://pypi.org/project/lean-interact/)
- [for Rocq](https://github.com/LLM4Rocq/pytanque)

Modules helping to interact with Isabelle server from Python are parts
of the [Proving for
Fun](https://github.com/maxhaslbeck/proving-contest-backends) project.

There are also clients to Isabelle server in other programming
languages, e.g. [this one in
Rust](https://lib.rs/crates/isabelle-client).

# Projects using the client

`isabelle-client` helped to build some cool LLM stuff (in
reversed chronological order):

- [TreeThink: A Modular Tree Search Library for Mathematical Reasoning
  with LLMs (Akbudak et
  al.)](https://doi.org/10.18653/2026.emnlp-demos.57) with
  [code](https://github.com/GGLAB-KU/treethink)
- [HybridProver: Augmenting Theorem Proving with LLM-Driven Proof
  Synthesis and Refinement (Hu et
  al.)](https://doi.org/10.18653/2026.findings-emnlp.1529) with
  [code](https://github.com/JilinHu/HybridProver)
- [Decompose-and-Formalise: Recursively Verifiable Natural Language
  Inference (Quan et al.)](https://doi.org/10.48550/arXiv.2601.19605)
- [Inferring Latent Intentions: Attributional Natural Language Inference
  in LLM Agents (Quan et
  al.)](https://doi.org/10.48550/arXiv.2601.08742)
- [StepProof: Step-by-step verification of natural language mathematical
  proofs (Hu et al.)](https://doi.org/10.48550/arXiv.2506.10558) with
  [code](https://github.com/r1nIGa/STEP-PROOF)
- [Verification and Refinement of Natural Language Explanations through
  LLM-Symbolic Theorem Proving (Quan et al., EMNLP
  2024)](https://doi.org/10.18653/v1/2024.emnlp-main.172) with
  [code](https://github.com/neuro-symbolic-ai/explanation_refinement)

# How to cite

If you're writing a research paper, you can cite the Isabelle client
using the [following DOI](https://doi.org/10.1007/978-3-031-16681-5_24).
You can also cite Isabelle 2021 (and an earlier version of the client)
with [this DOI](https://doi.org/10.1007/978-3-030-81097-9_20). There
also is a somewhat more complete (but unpublished)
[pre-print](https://arxiv.org/abs/2212.11173).

# How to Contribute

Please follow [the contribution
guide](https://isabelle-client.readthedocs.io/en/latest/contributing.html)
while adhering to [the code of
conduct](https://isabelle-client.readthedocs.io/en/latest/code-of-conduct.html).
