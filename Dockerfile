FROM alpine:3.3

ARG workdir=/opt/appr-server
RUN mkdir -p $workdir
ADD . $workdir
WORKDIR $workdir

RUN apk --no-cache --update add python py-pip openssl ca-certificates
RUN apk --no-cache --update add --virtual build-dependencies \
      python-dev build-base wget openssl-dev libffi-dev \
    && pip install pip -U \
    && pip install gunicorn -U && pip install -e . \
    && apk del build-dependencies build-base

CMD ["appr"]
# CMD ["./run-server.sh"]
