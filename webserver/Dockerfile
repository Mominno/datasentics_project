FROM httpd:2.4
COPY ./website /usr/local/apache2/htdocs/
# install app dependencies
#RUN apt-get update && apt-get install -y python3 python3-pip python3.11-venv
#COPY api.py .
#RUN python3 -m venv /opt/venv
#RUN /opt/venv/bin/pip install flask
EXPOSE 80
#CMD ["/opt/venv/bin/python", "./api.py"]
