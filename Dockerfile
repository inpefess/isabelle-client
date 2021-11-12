FROM makarius/isabelle:Isabelle2021
ENV HOME=/home/isabelle
ENV PATH=${HOME}/.local/bin:${HOME}/Isabelle/bin:${PATH}
USER root
RUN apt-get update
RUN apt-get install -y python3-pip
USER isabelle
RUN pip install -U pip isabelle-client jupyterlab
COPY examples ${HOME}
ENTRYPOINT []
