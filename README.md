[![PyPI version](https://badge.fury.io/py/isabelle-client.svg)](https://badge.fury.io/py/isabelle-client) [![CircleCI](https://circleci.com/gh/inpefess/isabelle-client.svg?style=svg)](https://circleci.com/gh/inpefess/isabelle-client) [![Documentation Status](https://readthedocs.org/projects/isabelle-client/badge/?version=latest)](https://isabelle-client.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/inpefess/isabelle-client/branch/master/graph/badge.svg)](https://codecov.io/gh/inpefess/isabelle-client)

# Isabelle Client

A client for [Isabelle](https://isabelle.in.tum.de) server. For more information about the server see part 4 of [the Isabelle system manual](https://isabelle.in.tum.de/dist/Isabelle2021/doc/system.pdf).

For information on using this client see [documentation](https://isabelle-client.readthedocs.io).

# How to install

```bash
pip install isabelle-client
```

# How to start Isabelle server

```bash
isabelle server > server.info
```

since we'll need server info for connecting to it with this client. Or:

```Python
from isabelle_client.utils import start_isabelle_server

server_info, server_process = start_isabelle_server()
``` 

# How to connect to the server

```Python
from isabelle_client.utils import get_isabelle_client

isabelle = get_isabelle_client(server_info)
```

# How to send a command to the server

```Python
isabelle.session_build(dirs=["."], session="examples")
```

Note that this method returns only the last reply from the server.

# How to log all replies from the server

We can add a standard Python logger to the client:

```Python
import logging

isabelle.logger = logging.getLogger()
isabelle.logger.setLevel(logging.INFO)
isabelle.logger.addHandler(logging.FileHandler("out.log"))
```

Then all replies from the server will go to the file ``out.log``.

# Examples

For an example of using this package see the ``examples`` directory.

# Video example

![video tutorial](https://github.com/inpefess/isabelle-client/blob/master/examples/tty.gif).

# Contributing

Issues and PRs are welcome.

# How to cite

If you're writing a research paper, you can cite Isabelle client in the following way:

```bib
@InProceedings{10.1007/978-3-030-81097-9_20,
author={L{\'i}{\v{s}}ka, Martin and Lupt{\'a}k, D{\'a}vid and Novotn{\'y}, V{\'i}t and R{\r{u}}{\v{z}}i{\v{c}}ka, Michal and Shminke, Boris and Sojka, Petr and {\v{S}}tef{\'a}nik, Michal and Wenzel, Makarius},
editor={Kamareddine, Fairouz and Sacerdoti Coen, Claudio},
title={CICM'21 Systems Entries},
booktitle={Intelligent Computer Mathematics},
year={2021},
publisher={Springer International Publishing},
address={Cham},
pages={245--248},
abstract={This consolidated paper gives an overview of new tools and improvements of existing tools in the CICM domain that occurred since the last CICM conference.},
isbn={978-3-030-81097-9},
doi={10.1007/978-3-030-81097-9_20},
url={https://doi.org/10.1007/978-3-030-81097-9_20}
}
```
