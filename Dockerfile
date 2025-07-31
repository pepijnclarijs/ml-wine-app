# This dockerfile contains the specifications for creating a docker image. It is like a blueprint for the docker image.

# Set Base Image.
FROM python:3.11-slim

# Set working directory.
WORKDIR /ML-wine-quality

# Set environment variables
ENV PYTHONPATH=/ML-wine-quality

# Copy the requirements.
COPY requirements.txt .

# Install requirements and do not save cache to reduce size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container.
COPY . /ML-wine-quality/

# Document which ports the app will use.
EXPOSE 5000

# Run the application
CMD ["python", "api/main.py"]
