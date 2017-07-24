FROM alpine:latest

ENV workdir /opt/appr-server
RUN mkdir -p $workdir
RUN apk --no-cache --update add python py-pip openssl ca-certificates
RUN apk --no-cache --update add --virtual build-dependencies \
      python-dev build-base wget openssl-dev libffi-dev ca-certificates	libstdc++

WORKDIR $workdir
RUN pip install pip -U
RUN pip install gunicorn -U 
COPY . .
RUN python setup.py install
    

RUN appr plugins install helm
ENTRYPOINT ["appr"]
