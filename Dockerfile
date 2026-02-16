FROM makarius/isabelle:Isabelle2025_X11_Latex
USER root
RUN apt-get update
RUN apt-get install -y python3-venv
ENV HOME /home/isabelle
ENV ISABELLE_BIN /home/isabelle/Isabelle/bin
ENV PATH=${HOME}/.local/bin/:${ISABELLE_BIN}:${PATH}
COPY examples/ ${HOME}/isabelle-client-examples/
COPY pyproject.toml uv.lock README.rst ${HOME}
COPY src/ ${HOME}/src/
RUN chown -R isabelle:isabelle ${HOME}/isabelle-client-examples/
USER isabelle
WORKDIR ${HOME}
RUN python3 -m venv .venv
RUN .venv/bin/python3 -m pip install --no-cache-dir notebook jupyterlab .
ENTRYPOINT [".venv/bin/jupyter", "lab", "--ip", "0.0.0.0", "--NotebookApp.token=''"]
