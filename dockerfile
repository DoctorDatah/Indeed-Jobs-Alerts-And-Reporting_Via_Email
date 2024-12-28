# Use an official Python runtime as a parent image
FROM python:3.13.1-slim

# Set the working directory in the container
WORKDIR /

# Copy the current directory contents into the container
COPY . /

# Ensure necessary directories exist
RUN mkdir -p logs data 

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run main.py when the container launches
CMD ["python", "./app/main.py"]
