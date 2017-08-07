FROM quay.io/appr/appr:base

ENV workdir /opt/appr-server
RUN mkdir -p $workdir
RUN apk --no-cache --update add python py-pip openssl ca-certificates
RUN apk --no-cache --update add --virtual build-dependencies \
      python-dev build-base wget openssl-dev libffi-dev libstdc++
COPY . $workdir
WORKDIR $workdir
RUN pip install jsonnet
RUN pip install -e .

RUN /pyinstaller/pyinstaller.sh --onefile --noconfirm \
    --add-data "appr/jsonnet/:appr/jsonnet" \
    --onefile \
    --hidden-import _jsonnet \
    --log-level DEBUG \
    --clean \
    bin/appr


from alpine:latest
ARG with_kubectl=false
ENV HOME=/appr
RUN mkdir -p /opt/bin && mkdir -p /opt/bin/k8s && mkdir $HOME && mkdir -p $HOME/local
ENV PATH=${PATH}:/opt/bin:/opt/bin/k8s
RUN apk --no-cache add ca-certificates
ENV WITH_KUBECTL ${with_kubectl}
RUN if [ "$WITH_KUBECTL" = true ]; then \
    apk add --update curl && rm -rf /var/cache/apk/* \
    && curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x ./kubectl \
    && cp ./kubectl /opt/bin/k8s; \
    fi

WORKDIR /appr/local

COPY --from=0 /opt/appr-server/dist/appr /opt/bin
RUN appr plugins install helm

ENTRYPOINT ["appr"]
