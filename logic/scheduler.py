import os
import asyncio
from asyncio import sleep as asleep
from datetime import datetime
from datetime import time
from zoneinfo import ZoneInfo
from astral import LocationInfo
from astral.sun import sun
from dotenv import load_dotenv
from handler import Browser
from logger import logger
from config import Config
from .rule import Rule, RuleState, convertRuleStateToWarmtepompSettings
from .rules import *
from .alwinHome import AlwinHome
from .weatherApi import CurrentWeather

load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, 'tokens.env'))


class Scheduler:

    def __init__(self):
        self.stop = False
        self.browser = Browser()
        self.weatherApi = CurrentWeather()
        self.alwinHome = AlwinHome()
        coordinatesLat = os.getenv("COORDINATES_LAT")
        coordinatesLon = os.getenv("COORDINATES_LON")
        self._continue = False
        self._curentWarmtepompState = RuleState.NEUTRAL
        self._amsterdam_zone = ZoneInfo("Europe/Amsterdam")

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
            active_rule = None
            for rule in self.rules:
                active_rule = rule
                kwargs = await self.obtainInformation()
                ruleWarmtepompState = rule.warmtepompState(**kwargs)
                if ruleWarmtepompState != RuleState.NEUTRAL and warmtepompState == RuleState.NEUTRAL:
                    warmtepompState = ruleWarmtepompState
                if warmtepompState != RuleState.NEUTRAL: # and other states when added
                    break
            if active_rule is not None and warmtepompState != self.curentWarmtepompState:
                logger.info(f"Rule {active_rule.name} changes the state to {warmtepompState.name}")
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
            "temperatureOutsideHistory": await self.weatherApi.temperatureHistory,
            "dawn": await self.getDawn(),
            "dusk": await self.getDusk()
        }

        return kwargs

    async def getDusk(self) -> time:
        """Gets the dusk times"""
        try:
            location = LocationInfo(self.coordinatesLat, self.coordinatesLon)
            sunTimes = sun(location.observer, date=datetime.now().date())
            return sunTimes['sunset'].astimezone(self._amsterdam_zone).time()
        except Exception as e:
            logger.error(f"Error while getting sunset time: {e}")
            return time(19, 0)

    async def getDawn(self) -> time:
        """Gets the dawn time"""
        try:
            location = LocationInfo(self.coordinatesLat, self.coordinatesLon)
            sunTimes = sun(location.observer, date=datetime.now().date())
            return sunTimes['sunrise'].astimezone(self._amsterdam_zone).time()
        except Exception as e:
            logger.error(f"Error while getting sunrise time: {e}")
            return time(7, 0)

    async def applyRules(self, warmtepompState: RuleState):
        """Applies the rules to the warmtepomp

        Args:
            warmtepompState (RuleState): The current state of the warmtepomp
        """
        if warmtepompState != RuleState.NEUTRAL and warmtepompState != self.curentWarmtepompState:
            for _ in range(30):
                if self.browser.browser is None:
                    self.browser.get_set_warmtepompen(convertRuleStateToWarmtepompSettings(warmtepompState))
                    self.curentWarmtepompState = warmtepompState
                    return
                await asleep(1)
                if self.stop:
                    logger.warning("aborting applying rules due to stop")
            logger.warning("aborting browser after waiting for 30 seconds to apply new rules")
            self.browser.quit_browser()
            self.browser.get_set_warmtepompen(convertRuleStateToWarmtepompSettings(warmtepompState))
            self.curentWarmtepompState = warmtepompState

    def signalContinue(self):
        self._continue = True

    # TODO should make this so it reads from the actual state of the warmtepomp, rather than what it sets here
    @property
    def curentWarmtepompState(self) -> RuleState:
        """Gets the current state of the warmtepomp"""
        return self._curentWarmtepompState

    @curentWarmtepompState.setter
    def curentWarmtepompState(self, state: RuleState):
        self._curentWarmtepompState = state
        logger.info(f"Current warmtepomp state set to {state.name}")
