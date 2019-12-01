### 1. Get Linux
FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt .
### 2. Get Java via the package manager
RUN \
    apk update \
    && apk upgrade \
    && apk add --no-cache bash \
    && apk add --no-cache --virtual=build-dependencies unzip \
    && apk add --no-cache curl \
    && apk add --no-cache jpeg-dev zlib-dev \
    && apk add --no-cache libmemcached-dev zlib-dev \
    && apk add --no-cache openjdk8-jre && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps \
    && apk add ttf-dejavu




### 3. Get Python, PIP




####
#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it

#ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

####


#FROM python:3.7.5
#ENV PYTHONUNBUFFERED 1

#RUN pip3 install -r requirements.txt
