FROM python:3.10.2-bullseye
ARG FLASK_APP=chatroom
ARG FLASK_ENV=development
WORKDIR /usr/src/
COPY ./chatroom ./chatroom
COPY ./requirements.txt . 
COPY ./setup.py .
RUN pip install -r /usr/src/requirements.txt
RUN pip install -e .
RUN flask init-db
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
