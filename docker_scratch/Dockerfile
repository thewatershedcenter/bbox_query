FROM pdal/pdal:sha-3d20a4b9
LABEL maintainer="michaelhuggins@protonmail.com"
SHELL [ "/bin/bash", "--login", "-c" ]
WORKDIR /

# print version info
RUN echo "---------------------------------------------------------" \
    && cat /etc/*-release \
    && echo "---------------------------------------------------------"


RUN conda install -y geopandas --channel conda-forge

EXPOSE 8080