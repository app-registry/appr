FROM six8/pyinstaller-alpine:latest

ENV workdir /opt/appr-server
RUN mkdir -p $workdir
RUN apk --no-cache --update add python py-pip openssl ca-certificates
RUN apk --no-cache --update add --virtual build-dependencies \
      python-dev build-base wget openssl-dev libffi-dev
ADD . $workdir
WORKDIR $workdir

RUN pip install pip -U \
    && pip install gunicorn -U && pip install -e .

RUN /pyinstaller/pyinstaller.sh --onefile --noconfirm \
    --onefile \
    --log-level DEBUG \
    --clean \
    bin/appr


from alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=0 /opt/appr-server/dist/appr /usr/bin/
ENTRYPOINT ["appr"]
