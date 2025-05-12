FROM python:3.10-alpine

ENV FLASK_APP=webserver.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 80
COPY . .
WORKDIR /

CMD ["gunicorn", "--bind", "0.0.0.0:80", "webserver:app"]