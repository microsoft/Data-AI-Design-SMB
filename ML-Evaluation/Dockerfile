# Use an official Python runtime as a parent image
# Choose a version compatible with your development environment, e.g., 3.9, 3.10, 3.11
# Using a 'slim' variant reduces image size
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size
# --upgrade pip ensures you have the latest pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes app.py and the templates folder
COPY . .

# Make port 5000 available to the world outside this container
# Gunicorn defaults to 8000, but 5000 is common for Flask/web apps.
# Azure Container Apps/App Service will map this internal port to external ports (80/443).
EXPOSE 5000

# Define environment variables (optional, can also be set in Azure)
# ENV FLASK_APP=app.py # Not strictly necessary when using Gunicorn directly

# Command to run the application using Gunicorn
# Binds Gunicorn to listen on all interfaces (0.0.0.0) inside the container on port 5000
# 'app:app' means: look for the file 'app.py' and find the Flask app instance named 'app' within it.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]