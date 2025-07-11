# Use a PyTorch base image with CUDA support for GPU acceleration
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security best practices
RUN addgroup --system bittensor && adduser --system --ingroup bittensor bittensor

# Copy the requirements file and install dependencies
# Using --chown to set ownership to the non-root user
# This leverages Docker layer caching
COPY --chown=bittensor:bittensor requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY --chown=bittensor:bittensor . .

# Install the project in editable mode
# This allows for easier development and ensures all modules are found
RUN pip install -e .

# Switch to the non-root user
USER bittensor

# Expose the default API port for the miner
EXPOSE 8001

# Add a healthcheck to monitor the API status
# This requires a /health endpoint on the miner's API
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# The default command can be overridden when running the container
# This is just a placeholder
CMD ["/bin/bash"]