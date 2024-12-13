# Use an official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install poetry
RUN pip install poetry

# Install dependencies using poetry
RUN poetry install --no-dev

# Expose the port
EXPOSE 8080

# Command to run the application
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=8080"]
