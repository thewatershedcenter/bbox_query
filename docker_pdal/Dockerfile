FROM pdal/ubuntubase:latest
LABEL maintainer="michaelhuggins@protonmail.com"
SHELL [ "/bin/bash", "--login", "-c" ]
WORKDIR /

# print version info
RUN echo "---------------------------------------------------------" \
&& cat /etc/*-release \
&& echo "---------------------------------------------------------"

# 


COPY file.sh /
RUN  chmod 777 file.sh
ENTRYPOINT ["/file.sh"]
