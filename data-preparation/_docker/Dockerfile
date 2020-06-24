
FROM jupyter/datascience-notebook
USER root

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

USER $NB_UID
