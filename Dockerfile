# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    default-mysql-client \
    cron

# Set up locale
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y locales \
    && sed -i '/es_AR.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen
ENV LANG es_AR.UTF-8
ENV LANGUAGE es_AR:es
ENV LC_ALL es_AR.UTF-8

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


# Copy your project files into the container
COPY . /app/

# Expose the port your application runs on
EXPOSE 8000

