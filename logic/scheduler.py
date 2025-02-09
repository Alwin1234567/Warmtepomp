from .rule import Rule, RuleState, convertRuleStateToWarmtepompSettings
from .rules import *
from .alwinHome import AlwinHome
from .weatherApi import CurrentWeather
from asyncio import sleep as asleep
from handler import Browser
from logger import logger
from datetime import datetime
from config import Config
from astral import LocationInfo
from astral.sun import sun
from datetime import time
from dotenv import load_dotenv
import os
import asyncio

load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, 'tokens.env'))


class Scheduler:

    def __init__(self):
        self.stop = False
        self.browser = Browser()
        self.weatherApi = CurrentWeather()
        self.alwinHome = AlwinHome()
        coordinatesLat = os.getenv("COORDINATES_LAT")
        coordinatesLon = os.getenv("COORDINATES_LON")

        if not coordinatesLat or not coordinatesLon:
            logger.error("No coordinates found")
            raise FileNotFoundError("No coordinates found")
        
        self.coordinatesLat = float(coordinatesLat)
        self.coordinatesLon = float(coordinatesLon)

        self.rules = asyncio.run(self.getCheckedRules())

    def getRules(self) -> list[Rule]:
        rules = []
        for subclass in Rule.__subclasses__():
            rules.append(subclass())
        rules.sort(key=lambda rule: rule.priority, reverse=True)
        return rules
    
    async def getCheckedRules(self) -> list[Rule]:
        """Gets the rules that are checked"""
        rules = self.getRules()
        try:
            kwargs = await self.obtainInformation()
        except Exception as e:
            logger.error(f"Error while obtaining information: {e}")
            return []
        checkedRules = []
        for rule in rules:
            try:
                rule.warmtepompState(**kwargs)
                checkedRules.append(rule)
            except Exception as e:
                print(e)
                logger.error(f"{rule.name} failed with the arguments given")
        if len(checkedRules) == 0:
            logger.warning("No rules pass the checks")
        return checkedRules
    
    async def run(self):
        while not self.stop:
            warmtepompState = RuleState.NEUTRAL
            for rule in self.rules:
                kwargs = await self.obtainInformation()
                ruleWarmtepompState = rule.warmtepompState(**kwargs)
                if ruleWarmtepompState != RuleState.NEUTRAL and warmtepompState == RuleState.NEUTRAL:
                    warmtepompState = ruleWarmtepompState
                if warmtepompState != RuleState.NEUTRAL: # and other states when added
                    break
            await self.applyRules(warmtepompState)
            for _ in range(Config.SCHEDULER_INTERVAL):
                await asleep(1)
                if self.stop:
                    break
                if self._continue: # signal by sever when it got a message to do someting
                    self._continue = False
                    break
    

    async def obtainInformation(self) -> dict[str, any]:
        """Obtains the information needed to apply the rules"""
        kwargs = {
            "currentDateTime": datetime.now(),
            "alwinHome": self.alwinHome.isHome,
            "temperatureOutside": await self.weatherApi.currentTemperature,
            "dawn": await self.getDawn(),
            "dusk": await self.getDusk()
        }

        return kwargs

    async def getDusk(self) -> time:
        """Gets the dusk times"""
        try:
            location = LocationInfo(self.coordinatesLat, self.coordinatesLon)
            sunTimes = sun(location.observer, date=datetime.now().date())
            return sunTimes['dusk'].time()
        except Exception as e:
            logger.error(f"Error while getting dusk time: {e}")
            return time(19, 0)
    
    async def getDawn(self) -> time:
        """Gets the dawn time"""
        try:
            location = LocationInfo(self.coordinatesLat, self.coordinatesLon)
            sunTimes = sun(location.observer, date=datetime.now().date())
            return sunTimes['dawn'].time()
        except Exception as e:
            logger.error(f"Error while getting dawn time: {e}")
            return time(7, 0)
    
    async def applyRules(self, warmtepompState: RuleState):
        """Applies the rules to the warmtepomp
        
        Args:
            warmtepompState (RuleState): The current state of the warmtepomp
        """
        if warmtepompState != RuleState.NEUTRAL and warmtepompState != self.curentWarmtepompState:
            for _ in range(30):
                if self.browser.browser != None:
                    self.browser.get_set_warmtepompen(convertRuleStateToWarmtepompSettings(warmtepompState))
                    break
                await asleep(1)
                if self.stop:
                    logger.warning("aborting applying rules due to stop")
            logger.warning("aborting browser after waiting for 30 seconds to apply new rules")
            self.browser.quit_browser()
            self.browser.get_set_warmtepompen(convertRuleStateToWarmtepompSettings(warmtepompState))
            
    def signalContinue(self):
        self._continue = True

    @property
    def curentWarmtepompState(self) -> RuleState:
        pass
        
                
                