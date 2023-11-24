FROM python:3.8.2-buster
USER root
WORKDIR /home/livis
#ADD livis /home/
# COPY ./livis_requirements.txt /home/livis/livis_requirements.txt
COPY . /home/livis
RUN pip install --no-cache-dir -r livis_requirements.txt
#CMD /usr/local/bin/gunicorn --bind 0.0.0.0:8000 livis.wsgi --reload --workers 1 --timeout 60