FROM python:3.9-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements/base.txt /install/requirements.txt

RUN apk add --update \
        g++ \
        libxml2 \
        libxml2-dev &&\
    apk add libxslt-dev
RUN pip install --prefix=/install -r /install/requirements.txt

FROM base

ENV INSTALL_PATH /sunsetter
RUN mkdir ${INSTALL_PATH}
WORKDIR ${INSTALL_PATH}

ARG GIT_COMMIT_SHA1_BUILD
ENV GIT_COMMIT_SHA1=${GIT_COMMIT_SHA1_BUILD}

ENV PORT=8000
EXPOSE ${PORT}

ENV MAPS_API=""
ENV SENTRY_DSN=""

COPY --from=builder /install /usr/local

COPY . .

ENTRYPOINT [ "sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --access-logfile - app:app" ]
