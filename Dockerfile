"""
Dockerfile - Container Definition for Youth Group API

This file defines how to build a Docker container that runs the FastAPI application.
Docker containers package an application with all its dependencies into a portable unit.

Build Process:
1. Start with a base Python image (contains Python runtime)
2. Set up working directory
3. Install dependencies from requirements.txt
4. Copy application code
5. Configure networking and environment
6. Define startup command

To build: docker build -t youth-group-api .
To run: docker run -p 8099:8099 youth-group-api
"""

# Use an official Python runtime as a parent image
# python:3.11-slim is a lightweight Python 3.11 image (smaller than full Python image)
FROM python:3.11-slim

# Set the working directory in the container
# All subsequent commands (COPY, RUN, etc.) will execute in this directory
WORKDIR /app

# Copy the requirements file into the container at /app
# This is done BEFORE copying code so Docker can cache this layer
# If code changes but requirements don't, Docker reuses the cached pip install layer
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Don't store pip cache (reduces final image size)
# This installs all Python dependencies needed by the application
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
# This copies all files from current directory (.) to /app in container
# Done AFTER requirements so code changes don't invalidate pip install cache
COPY . /app

# Make port 8099 available to the world outside this container
# This documents which port the app uses (doesn't actually open it - that's done with -p flag)
EXPOSE 8099

# Define environment variables for non-secret configuration
# DB_HOST is set to "host.docker.internal" to help the container connect 
# to services running on the host machine (useful for Docker Desktop on Mac/Windows)
# This allows the containerized app to connect to MySQL running on your local machine
ENV DB_HOST="host.docker.internal"

# Run uvicorn server when container starts
# This is the command executed when you run the container
# --host 0.0.0.0: Makes server accessible from outside container (not just localhost)
# --port 8099: Port the server listens on
# --app-dir /app: Sets working directory so Python can find modules
# youthGroupFastAPI:app: Module name (youthGroupFastAPI.py) and app object name
CMD ["uvicorn", "youthGroupFastAPI:app", "--host", "0.0.0.0", "--port", "8099", "--app-dir", "/app"]

