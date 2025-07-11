# Use a PyTorch base image with CUDA support for GPU acceleration
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
# This leverages Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install the project in editable mode
# This allows for easier development and ensures all modules are found
RUN pip install -e .

# Expose the default API port
EXPOSE 8001

# The default command can be overridden when running the container
# This is just a placeholder
CMD ["/bin/bash"]