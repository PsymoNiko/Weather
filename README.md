<h1>Getting API Key from OpenWeather.org</h1>

Go to https://openweathermap.org/ and create an account.
After logging in, go to the API keys section under your account settings.
Generate a new API key or copy an existing one.

<h1>Installing Docker and Running Celery with Docker Compose</h1>


    sudo apt-get update
    sudo apt-get install docker.io

# Then run thi son your terminal
    
    docker-compose up

Note: Make sure to replace the values for CELERY_BROKER_URL, API_KEY and CITY_NAME in the main.py file with your own values.
________________________________________________________

<h1>Another way to run the program</h1>

1) Run redis on your docker:
    
    

    docker run --name redis-connection -p 6370:6379 -d redis

2) Run celery and celery beat:


    celery -A main worker -B -l INFO

3) Open a python compiler:

    
    from main import *
    city = city_request('you city')

# Congrats, Now you can see temperature  from cache without waiting for requests