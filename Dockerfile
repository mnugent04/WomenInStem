# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app

# Make port 8099 available to the world outside this container
EXPOSE 8099

# Define environment variables for non-secret configuration
# DB_HOST is set to "host.docker.internal" to help the container connect 
# to services running on the host machine (useful for Docker Desktop on Mac/Windows)
ENV DB_HOST="host.docker.internal"

# Run uvicorn server
# The --host 0.0.0.0 makes the server accessible from outside the container.
# We use --app-dir to add the 'python' directory to the PYTHONPATH so modules can be found.

CMD ["uvicorn", "youthGroupFastAPI:app", "--host", "0.0.0.0", "--port", "8099", "--app-dir", "/app"]

