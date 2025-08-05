# Use slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /ml-wine-app

# Set environment variable for Python path
ENV PYTHONPATH=/ml-wine-app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy project metadata files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (properly from lockfile)
RUN uv sync --no-cache

# Copy the rest of the application code
COPY . .

# Expose the port your API uses
EXPOSE 80

# Run the application
CMD ["uv", "run", "python", "api/main.py"]
