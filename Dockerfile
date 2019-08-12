FROM alpine:3.10
RUN apk add --no-cache --virtual python3-dev && \
    apk add --no-cache --update python3 && \
    pip3 install --upgrade pip setuptools && \
    pip3 install --upgrade requests==2.8.1

ENV HARVEST_ACCESS_TOKEN ''
ENV HARVEST_ACCOUNT_ID ''
ENV TEMPLATE_FILE_NAME 'template.json'
COPY omnomnom.py .
COPY $TEMPLATE_FILE_NAME .

CMD ["python3", "omnomnom.py" ]

