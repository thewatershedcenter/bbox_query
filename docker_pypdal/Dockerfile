FROM pdal/pdal:sha-3d20a4b9
LABEL maintainer="michaelhuggins@protonmail.com"
SHELL [ "/bin/bash", "--login", "-c" ]
WORKDIR /

# print version info
RUN echo "---------------------------------------------------------" \
    && cat /etc/*-release \
    && echo "---------------------------------------------------------"

# onstall pdal
RUN conda install -y -c conda-forge numba \
    entwine \
    dask \
    geopandas \
    h5py \
    laspy=2.0.3 \
    laz-perf=2.1.0 \
    numba \
    pandas \
    pytables \
    python-pdal=2.4.2 \
    shapely 

COPY app_ept2.py /
RUN  chmod 777 /app_ept2.py
ENTRYPOINT ["python", "/app_ept2.py"]
