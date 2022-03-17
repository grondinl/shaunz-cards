FROM python:3.10-alpine

RUN apk add linux-headers build-base && \
    pip install flask requests prometheus_client uwsgi

COPY main.py . 

ENTRYPOINT [ "uwsgi" ]

CMD ["--http", "0.0.0.0:8000", \
    "--wsgi-file", "main.py", \
    "--callable", "app"]

