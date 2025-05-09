FROM python:3.10-alpine

ENV FLASK_APP=model_api.py
ENV FLASK_RUN_HOST=0.0.0.0


#RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
#CMD ["python", "./api.py"]
CMD ["flask", "run", "--debug"]