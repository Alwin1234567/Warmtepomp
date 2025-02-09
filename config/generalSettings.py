from datetime import time

class Config:
    OUTSIDE_TEMPERATURE_UPDATE_INTERVAL = 15 # minutes
    SCHEDULER_INTERVAL = 60 # seconds
    WEEKDAYS = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    DEFAULT_DAWN = time(7, 0)
    DEFAULT_DUSK = time(19, 0)
    DEFAULT_OUTSIDE_TEMPERATURE = 20.0
    DEFAULT_ALWIN_TIME_OFF = time(23, 0)
    DEFAULT_ALWIN_TIME_ON = time(3, 0)
    COLD_OUTSIDE_TEMPERATURE_THRESHOLD = 5.0
