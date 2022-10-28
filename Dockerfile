FROM makarius/isabelle:Isabelle2022
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
USER root
RUN groupmod -g 9999 isabelle
RUN usermod -u 9999 -g 9999 isabelle
RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
RUN apt-get update
RUN apt-get install -y python3-pip netcat
ENV HOME /home/${NB_USER}
ENV ISABELLE_BIN /home/isabelle/Isabelle/bin/
ENV PATH=${HOME}/.local/bin/:${ISABELLE_BIN}:${PATH}
COPY examples/ ${HOME}/isabelle-client-examples/
RUN chown -R ${NB_USER}:${NB_USER} ${HOME}/isabelle-client-examples/
RUN chown -R ${NB_USER}:${NB_USER} ${ISABELLE_BIN}
USER ${NB_USER}
WORKDIR ${HOME}
RUN python3 -m pip install --no-cache-dir notebook jupyterlab isabelle-client
ENTRYPOINT []
