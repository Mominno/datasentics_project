FROM python:3.10-alpine

ENV FLASK_APP=api.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .

CMD ["flask", "run", "--debug"]