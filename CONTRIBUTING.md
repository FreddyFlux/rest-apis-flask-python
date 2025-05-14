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

## Adding a script to the build process to run migration upgrades
We remove from "Dockerfile": 
```
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:create_app()"]
``` 

And add a file called "docker-entrypoint.sh"
Where we add the script: 
```
#!/bin/sh

flask db upgrade

exec gunicorn -b 0.0.0.0:80 "app:create_app()"
```

And add to the "Dockerfile":
```
CMD ["/bin/bash", "./docker-entrypoint.sh"]
```