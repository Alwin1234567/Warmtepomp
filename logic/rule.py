from abc import ABC, abstractmethod
from enum import Enum
from config import WarmtepompSettings as WS

class RuleState(Enum):
    NEUTRAL = 0
    AUTO = 1
    OFF = 2

# Mapping from RuleState to WarmtepompSettings
RULE_STATE_TO_WARMTEPOMP_SETTINGS = {
    RuleState.AUTO: WS.AUTO,
    RuleState.OFF: WS.OFF
}

def convertRuleStateToWarmtepompSettings(rule_state: RuleState) -> WS:
    try:
        return RULE_STATE_TO_WARMTEPOMP_SETTINGS[rule_state]
    except KeyError:
        raise ValueError(f"cannont convert {rule_state} to WarmtepompSettings")

class Rule(ABC):
    """Abstract class for a rule"""
    @abstractmethod
    def warmtepompState(self, **kwargs) -> RuleState:
        """Returns the state of the warmtepomp NEUTRAL means the rule is to be ignored"""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """Returns the priority of the rule, higher priority rules will go first"""
        pass

    @property
    def name(self) -> str:
        """Returns the name of the rule"""
        return self.__class__.__name__
