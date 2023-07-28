# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential sqlite3

ADD ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r /app/requirements.txt

RUN pip install easycompletion==0.3.2

# Add the parent directory contents into the container at /app
ADD ./start.py /app/start.py
ADD ./tinyagi /app/tinyagi

CMD python /app/start.py