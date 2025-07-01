# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port (Render uses 10000 by default for Docker)
EXPOSE 10000

# Start the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app.main:app"]