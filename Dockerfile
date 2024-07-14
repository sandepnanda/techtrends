# Use a Python base image in version 3.8
FROM python:3.8-slim
LABEL maintainer="Sandep Nanda"

# Set the working directory
WORKDIR /app

# Copy the requirements file and install packages
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./techtrends /app

# Expose the application port
EXPOSE 3111

# Initialize the database
RUN python init_db.py

# Set the environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "app.py"]
