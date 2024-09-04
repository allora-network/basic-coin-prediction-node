FROM python:3.11-slim as project_env

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools \
    && pip install -r requirements.txt

FROM project_env

COPY . /app/

# Set the entrypoint command
CMD ["gunicorn", "--conf", "/app/gunicorn_conf.py", "main:app"]
