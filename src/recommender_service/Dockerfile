FROM python:3.10-alpine

ENV FLASK_APP=model_api.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["flask", "run", "--debug"]