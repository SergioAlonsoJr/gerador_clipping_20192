FROM python:3-alpine
WORKDIR /usr/src/app
COPY requirements.txt .
RUN apk update 
RUN apk upgrade
RUN apk add --no-cache bash 
RUN apk add --no-cache --virtual=build-dependencies unzip 
RUN apk add --no-cache curl 
RUN apk add --no-cache jpeg-dev zlib-dev 
RUN apk add --no-cache libmemcached-dev zlib-dev 
RUN apk add --no-cache openjdk8-jre 
RUN apk add --no-cache poppler-utils 
RUN apk add --no-cache postgresql-libs 
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN apk add ttf-dejavu
RUN apk add terminus-font
RUN python3 -m pip install -r requirements.txt --no-cache-dir
RUN apk --purge del .build-deps 