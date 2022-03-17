FROM python:3.10-alpine

RUN pip install flask requests prometheus_client uwsgi

COPY app.py . 

CMD ["uwsgi", "app.py"]
