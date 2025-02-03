from .rule import Rule, RuleState
from datetime import time

"""Rules for the warmtepomp

Args:
    currentTime (time): The current time

Kwargs:
    alwinHome (bool): Whether Alwin is home
    temperatureOutside (float): The temperature outside
    dawn (time): The time the sun rises
    dusk (time): The time the sun sets
"""

class RuleDefualt(Rule):
    def warmtepompState(self, *args, **kwargs) -> RuleState:
        return RuleState.AUTO
    
    @property
    def priority(self):
        return 0

class RuleOptimiseEnergy(Rule):
    def warmtepompState(self, currentTime: time, *args, dawn: time = time(7,0), dusk: time = time(19,0), **kwargs) -> RuleState:
        if currentTime < dawn or currentTime > dusk:
            return RuleState.OFF
        return RuleState.NEUTRAL

    @property
    def priority(self):
        return 10
    
class RuleColdOutside(Rule):
    def warmtepompState(self, *args, temperatureOutside: float = 20, **kwargs) -> RuleState:
        if temperatureOutside < 5:
            return RuleState.AUTO
        return RuleState.NEUTRAL
    
    @property
    def priority(self):
        return 50

class RuleAlwinHome(Rule):
    def warmtepompState(self, currentTime: time, *args, alwinHome = False, **kwargs) -> RuleState:
        if not alwinHome:
            return RuleState.NEUTRAL
        if currentTime >= time(23, 0) or currentTime <= time(3, 0):
            return RuleState.OFF
        return RuleState.NEUTRAL
    
    @property
    def priority(self):
        return 70

