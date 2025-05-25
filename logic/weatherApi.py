from config import Config
import requests
from dotenv import load_dotenv
import os
from logger import logger
from datetime import datetime, timedelta


load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, '.env'))

class CurrentWeather:

    def __init__(self):
        self.weatherApiToken = os.getenv('WEATHERAPI')
        self.updateInterval = timedelta(minutes=Config.OUTSIDE_TEMPERATURE_UPDATE_INTERVAL)

        if not self.weatherApiToken:
            logger.error("No weather api token found")
            self._hasToken = False
        else:
            self._hasToken = True
        self._temperature = 20.0
        self._lastUpdate = datetime(1970, 1, 1)

        coordinatesLat = os.getenv("COORDINATES_LAT")
        coordinatesLon = os.getenv("COORDINATES_LON")

        if not coordinatesLat or not coordinatesLon:
            logger.error("No coordinates found")
            raise FileNotFoundError("No coordinates found")

        self.coordinatesLat = float(coordinatesLat)
        self.coordinatesLon = float(coordinatesLon)

        self._temperature_history = [Config.DEFAULT_OUTSIDE_TEMPERATURE] * Config.OUTSIDE_TEMPERATURE_HISTORY_SIZE



    async def requestTemperature(self) -> float:
        if not self.hasToken:
            return 20.0
        url = 'http://api.weatherapi.com/v1/current.json'
        params = {
            'key' : self.weatherApiToken,
            'q' : f'{self.coordinatesLat}, {self.coordinatesLon}',
            'aqi': 'no'
        }
        response = requests.get(url, params=params)
        data = response.json()
        try :
            temperature = data['current']['temp_c']
        except KeyError:
            logger.error(f"Error while getting temperature from weather api: {data}")
            temperature = 20.0
        return temperature

    async def setTemperature(self):
        try:
            self._temperature = await self.requestTemperature()
            await self.updateHistory(self._temperature)
            logger.debug(f"Temperature set to {self._temperature}")
        except Exception as e:
            logger.error(f"Error while setting temperature: {e}")
            self._temperature = 20.0
        self._lastUpdate = datetime.now()

    async def updateHistory(self, temperature: float):
        try:
            self._temperature_history.append(temperature)
            self._temperature_history.pop(0)
        except Exception as e:
            logger.error(f"Error while updating temperature history: {e}")

    @property
    def hasToken(self) -> bool:
        return self._hasToken

    @property
    async def currentTemperature(self) -> float:
        if not self.hasToken:
            return Config.DEFAULT_OUTSIDE_TEMPERATURE
        if datetime.now() - self._lastUpdate > self.updateInterval:
            await self.setTemperature()
        return self._temperature

    @property
    async def temperatureHistory(self) -> list[float]:
        if not self.hasToken:
            return [Config.DEFAULT_OUTSIDE_TEMPERATURE] * Config.OUTSIDE_TEMPERATURE_HISTORY_SIZE
        if datetime.now() - self._lastUpdate > self.updateInterval:
            await self.setTemperature()
        return self._temperature_history
