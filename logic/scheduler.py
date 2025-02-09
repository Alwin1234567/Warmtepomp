from .rule import Rule, RuleState, convertRuleStateToWarmtepompSettings
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


class Scheduler:

    def __init__(self):
        rules = self.getRules()
        self.stop = False
        self.rules = rules
        self.browser = Browser()
        self.weatherApi = CurrentWeather()
        self.alwinHome = AlwinHome()

    def getRules(self) -> list[Rule]:
        rules = []
        for subclass in Rule.__subclasses__():
            rules.append(subclass())
        rules.sort(key=lambda rule: rule.priority, reverse=True)
        return rules
    
    async def run(self):
        while not self.stop:
            warmtepompState = RuleState.NEUTRAL
            for rule in self.rules:
                args, kwargs = await rule.obtainInformation() # this needs fixing
                ruleWarmtepompState = rule.warmtepompState(*args, **kwargs)
                if ruleWarmtepompState != RuleState.NEUTRAL and warmtepompState == RuleState.NEUTRAL:
                    warmtepompState = ruleWarmtepompState
                if warmtepompState != RuleState.NEUTRAL:
                    break
            await self.applyRules(warmtepompState)
            for _ in range(Config.SCHEDULER_INTERVAL):
                await asleep(1)
                if self.stop:
                    break
                if self._continue # signal by sever when it got a message to do someting
                    break
    

    async def obtainInformation(self):
        """Obtains the information needed to apply the rules"""
        # args
        args = {
            "currentTime": datetime.now().time()
        }

        # kwargs
        kwargs = {
            "alwinHome": self.alwinHome.isHome,
            "temperatureOutside": await self.weatherApi.currentTemperature,
            "dawn": await self.getDawn(),
            "dusk": await self.getDusk()
        }

    async def getDusk(self):
        """Gets the dusk times"""
        try:
            location = LocationInfo(Config.COORDINATES[0], Config.COORDINATES[1])
            sunTimes = sun(location.observer, date=datetime.now().date())
            return sunTimes['dusk']
        except Exception as e:
            logger.error(f"Error while getting dusk time: {e}")
            return time(19, 0)
    
    async def getDawn(self):
        """Gets the dawn time"""
        try:
            location = LocationInfo(Config.COORDINATES[0], Config.COORDINATES[1])
            sunTimes = sun(location.observer, date=datetime.now().date())
            return sunTimes['dawn']
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
            


    @property
    def curentWarmtepompState(self) -> RuleState:
        pass
        
                
                