FROM python:3.10-alpine
# WORKDIR /code

ENV FLASK_APP=api.py
ENV FLASK_RUN_HOST=0.0.0.0

#RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
COPY index.html /templates/index.html
#CMD ["python", "./api.py"]
CMD ["flask", "run", "--debug"]