# Base image with Python
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libmariadb-dev \
    pkg-config \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install --no-dev

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=8080"]
