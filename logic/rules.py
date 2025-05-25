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
    def warmtepompState(self, temperatureOutsideHistory: list[float] = [Config.DEFAULT_OUTSIDE_TEMPERATURE] * Config.OUTSIDE_TEMPERATURE_HISTORY_SIZE, **kwargs) -> RuleState:
        smaller_history_size = min(len(temperatureOutsideHistory), Config.COLD_OUTSIDE_HISTORY_SIZE)
        smaller_history = temperatureOutsideHistory[-smaller_history_size:]
        for temperature in smaller_history:
            if temperature >= Config.COLD_OUTSIDE_TEMPERATURE_THRESHOLD:
                return RuleState.NEUTRAL
        return RuleState.AUTO

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
