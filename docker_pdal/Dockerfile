FROM pdal/pdal:sha-3d20a4b9
LABEL maintainer="michaelhuggins@protonmail.com"
SHELL [ "/bin/bash", "--login", "-c" ]
WORKDIR /

# print version info
RUN echo "---------------------------------------------------------" \
    && cat /etc/*-release \
    && echo "---------------------------------------------------------"


RUN conda install -y geopandas dask --channel conda-forge

COPY file_ept.sh /
COPY app_ept.py /
RUN  chmod 777 /file_ept.sh && chmod 777 /app_ept.py
ENTRYPOINT ["python", "/app_ept.py"]
