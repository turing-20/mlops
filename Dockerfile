# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project code into the container
COPY . /code/

# Expose the port that Django runs on
EXPOSE 8000

# Run Django development server
RUN chmod +x server-start.sh

CMD ["/bin/sh", "./server-start.sh"]
