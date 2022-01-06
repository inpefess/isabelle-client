FROM makarius/isabelle:Isabelle2021-1
ENV HOME=/home/isabelle
ENV PATH=${HOME}/.local/bin:${HOME}/Isabelle/bin:${PATH}
USER root
RUN apt-get update
RUN apt-get install -y python3-pip
COPY examples ${HOME}/isabelle-client-examples
RUN chown -R isabelle ${HOME}/isabelle-client-examples
USER isabelle
RUN pip install -U pip jupyterlab
COPY isabelle_client ${HOME}/isabelle_client
COPY pyproject.toml ${HOME}
COPY poetry.lock ${HOME}
COPY README.rst ${HOME}
RUN pip install .
ENTRYPOINT []
