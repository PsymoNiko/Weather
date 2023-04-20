import os
import redis
import requests
from celery import Celery
from typing import List, Union, Tuple

from dotenv import load_dotenv

load_dotenv()

app = Celery('main', backend='redis://localhost:6370', broker='redis://localhost:6370/0')
app.config_from_object('schedules')


def city_request(city: str) -> Union[int, str]:
    redis_connection = redis.Redis(host="localhost", port=6370, db=0, decode_responses=True, charset='UTF-8')
    city_temp = redis_connection.get(f'temp_{city}')
    if city_temp is not None:
        return int(city_temp)
    try:
        response = requests.get('https://api.openweathermap.org/data/2.5/weather',
                                {"q": {city}, "appid": {os.environ.get('API_KEY')}})
        temp = int(response.json()['main']['temp']) - 273
        redis_connection.set(f'temp_{city}', temp, ex=60)
        return temp
    except ConnectionError:
        return 'You lost your Internet connection!!!'


@app.task
def some_cities(*args) -> List[Tuple[str, Union[int, str]]]:
    cities: List[str] = ['tehran', 'joybar', 'gorgan', 'mashhad', 'tabriz',
                         'london', 'liverpool', 'madrid', 'munich', 'shiraz',
                         'ardebil']

    mapping: List[Tuple[str, Union[int, str]]] = [(city, city_request(city)) for city in cities]
    return mapping
