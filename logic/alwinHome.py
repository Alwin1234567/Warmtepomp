import asyncio
from datetime import datetime, timedelta
from logger import logger
from config import Config, FallAsleepEnum


class AlwinHome:
    """Singleton class to keep track of whether Alwin is home"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._isHome = False
        self._setAwayTask = None
        self._fallingAsleep = FallAsleepEnum.NEUTRAL

    def setHome(self, dayStr: str = "sunday"):
        self._isHome = True
        logger.info(f"Set Alwin to is home until next {dayStr}")
        if self._setAwayTask:
            self._setAwayTask.cancel()
        try:
            day = self.dayToIndex(dayStr)
        except ValueError as e:
            logger.error(e)
            day = 6
        self._setAwayTask = asyncio.create_task(self._schedule_setAway_next_sunday(day))

    def setAway(self):
        if self._setAwayTask:
            self._setAwayTask.cancel()
            self._setAwayTask = None
        if not self._isHome:
            return
        logger.info("Set Alwin to is away")
        self._isHome = False

    def startWinterSleep(self):
        if self._fallingAsleep != FallAsleepEnum.NEUTRAL:
            logger.info("Alwin is already falling asleep or asleep")
            return
        logger.info("Set Alwin to falling asleep")
        asyncio.create_task(self._schedule_winter_sleep())

    def dayToIndex(self, day: str) -> int:
        """Converts the day to an index

        Args:
            day (str): The day to convert

        Returns:
            int: The index of the day
        """
        days = {
            "sunday": 0,
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5,
            "saturday": 6
        }
        try:
            return days[day.lower()]
        except KeyError:
            raise ValueError(f"Invalid day: {day}")

    async def _schedule_setAway_next_sunday(self, day: int):
        """Schedules setAway to run at the next specified day at 12 PM

        Args:
            day (int): The day to schedule the setAway task
        """
        now = datetime.now()
        daysUntilAway = (day - now.weekday()) % 7

        if daysUntilAway == 0:
            daysUntilAway = 7
        nextDayAway = now + timedelta(days=daysUntilAway)
        nextDayAway = nextDayAway.replace(hour=12, minute=0, second=0, microsecond=0)
        delay = (nextDayAway - now).total_seconds()
        await asyncio.sleep(delay)
        self.setAway()

    async def _schedule_winter_sleep(self):
        """Schedules Warmtepomp to go back on after falling asleep in winter"""
        self._fallingAsleep = FallAsleepEnum.FALLING_ASLEEP
        sleep_delay = Config.DEFAULT_ALWIN_TIME_TO_SLEEP * 60 # minutes to seconds
        scheduler_delay = Config.SCHEDULER_INTERVAL * 4 # seconds
        await asyncio.sleep(sleep_delay)
        self._fallingAsleep = FallAsleepEnum.ASLEEP

        await asyncio.sleep(scheduler_delay)
        self._fallingAsleep = FallAsleepEnum.NEUTRAL

    @property
    def isHome(self):
        return self._isHome

    @property
    def fallingAsleep(self):
        return self._fallingAsleep
