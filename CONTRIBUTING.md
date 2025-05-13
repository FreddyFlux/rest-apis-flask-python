# CONTRIBUTING

## How to run the Dockerfile locally
#### With a local env based Dockerfile: 
``` 
FROM python:3.13
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]
``` 

#### With LIVE Dockerfile and "overstearing" the CMD line in it to use "flask run" instead of Gunicorn
``` 
$ docker run -dp 5005:5000 -w //app -v "//$(pwd)://app" flask-smorest-api sh -c "flask run"
``` 
