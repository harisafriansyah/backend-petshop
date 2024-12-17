# Base image with Python
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libmariadb-dev \
    libpq-dev \
    pkg-config \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Poetry
RUN pip install poetry

# Add psycopg2-binary
RUN poetry add psycopg2-binary

# Install dependencies using Poetry
RUN poetry install --no-dev

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=${PORT:-8000}"]
