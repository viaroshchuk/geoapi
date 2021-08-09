FROM python:3.8

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/src/app"

WORKDIR /src
ADD . /src/
RUN pip3 install -r /src/requirements.txt

EXPOSE 8080
