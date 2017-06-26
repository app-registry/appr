FROM six8/pyinstaller-alpine:latest

ENV workdir /opt/appr-server
RUN mkdir -p $workdir
ADD . $workdir
WORKDIR $workdir

RUN apk --no-cache --update add python py-pip openssl ca-certificates
RUN apk --no-cache --update add --virtual build-dependencies \
      python-dev build-base wget openssl-dev libffi-dev \
    && pip install pip -U \
    && pip install gunicorn -U && pip install -e . \
    && apk del build-dependencies build-base
RUN /pyinstaller/pyinstaller.sh --onefile --noconfirm \
    --onefile \
    --log-level DEBUG \
    --clean \
    bin/appr


FROM alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=0 /opt/appr-server/dist/appr /usr/bin/


CMD ["appr"]
# CMD ["./run-server.sh"]
