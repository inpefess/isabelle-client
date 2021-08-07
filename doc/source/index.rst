..
  Copyright 2021 Boris Shminke

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

##########################################
Welcome to Isabelle client documentation!
##########################################

A client for `Isabelle`_ server. For more information about the server see part 4 of `the Isabelle system manual`_.

Getting started
****************

The best way to install this client is to use ``pip``::

    pip install isabelle-client

Then follow :ref:`usage-example` or run `the script`_

If you're writing a research paper, you can cite Isabelle client (and Isabelle 2021) in the following way::

  @inproceedings{DBLP:conf/mkm/LiskaLNRSSSW21,
  author    = {Martin L{\'{\i}}ska and
  D{\'{a}}vid Lupt{\'{a}}k and
  V{\'{\i}}t Novotn{\'{y}} and
  Michal Ruzicka and
  Boris Shminke and
  Petr Sojka and
  Michal Stef{\'{a}}nik and
  Makarius Wenzel},
  editor    = {Fairouz Kamareddine and
  Claudio Sacerdoti Coen},
  title     = {CICM'21 Systems Entries},
  booktitle = {Intelligent Computer Mathematics - 14th International Conference,
  {CICM} 2021, Timisoara, Romania, July 26-31, 2021, Proceedings},
  series    = {Lecture Notes in Computer Science},
  volume    = {12833},
  pages     = {245--248},
  publisher = {Springer},
  year      = {2021},
  url       = {https://doi.org/10.1007/978-3-030-81097-9\_20},
  doi       = {10.1007/978-3-030-81097-9\_20},
  timestamp = {Wed, 21 Jul 2021 15:51:07 +0200},
  biburl    = {https://dblp.org/rec/conf/mkm/LiskaLNRSSSW21.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
  }

.. toctree::
   :maxdepth: 2
   :caption: Contents:
	     
   usage-example
   how-to-contribute
   package-documentation

Indices and tables
*******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Isabelle: https://isabelle.in.tum.de
.. _the Isabelle system manual: https://isabelle.in.tum.de/dist/Isabelle2021/doc/system.pdf
.. _the script: https://github.com/inpefess/isabelle-client/blob/master/examples/example.py
