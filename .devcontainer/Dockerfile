# Update the Dockerfile to fix the uv PATH issue

# Use Ubuntu as a base image
FROM ubuntu:20.04

# Set environment variables
env DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv using pip and configure PATH
RUN pip3 install uv

# Ensure the installed path is in the PATH for appuser
RUN echo 'export PATH="$PATH:/usr/local/bin"' >> /home/appuser/.bashrc

# Set the default user as appuser
USER appuser

# Command to run the application
CMD ["python3", "app.py"]