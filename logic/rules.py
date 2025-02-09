from .rule import Rule, RuleState
from datetime import datetime, time
from config import Config

"""Rules for the warmtepomp

Kwargs:
    currentDateTime (datetime): The current time
    alwinHome (bool): Whether Alwin is home
    temperatureOutside (float): The temperature outside
    dawn (time): The time the sun rises
    dusk (time): The time the sun sets
"""

class RuleDefualt(Rule):
    def warmtepompState(self, **kwargs) -> RuleState:
        return RuleState.AUTO
    
    @property
    def priority(self):
        return 0

class RuleOptimiseEnergy(Rule):
    def warmtepompState(self, currentDateTime: datetime, dawn = Config.DEFAULT_DAWN, dusk = Config.DEFAULT_DUSK, **kwargs) -> RuleState:
        if currentDateTime.time() < dawn or currentDateTime.time() > dusk:
            return RuleState.OFF
        return RuleState.NEUTRAL

    @property
    def priority(self):
        return 10
    
class RuleColdOutside(Rule):
    def warmtepompState(self, temperatureOutside: float = Config.DEFAULT_OUTSIDE_TEMPERATURE, **kwargs) -> RuleState:
        if temperatureOutside < Config.COLD_OUTSIDE_TEMPERATURE_THRESHOLD:
            return RuleState.AUTO
        return RuleState.NEUTRAL
    
    @property
    def priority(self):
        return 50

class RuleAlwinHome(Rule):
    def warmtepompState(self, currentDateTime: datetime, alwinHome = False, **kwargs) -> RuleState:
        if not alwinHome:
            return RuleState.NEUTRAL
        if currentDateTime.time() >= Config.DEFAULT_ALWIN_TIME_OFF or currentDateTime.time() <= Config.DEFAULT_ALWIN_TIME_ON:
            return RuleState.OFF
        return RuleState.NEUTRAL
    
    @property
    def priority(self):
        return 70

