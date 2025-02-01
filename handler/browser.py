from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from config import WarmtepompSettings
from logger import logger
import os


class Browser():
    """Class that uses Selenium to interact with the web interface of the heat pump"""
    
    def __init__(self):
        self.browser = None
        self.loading = None
        logger.debug("Browser instance created")

        # Check for geckodriver.exe and geckodriver
        geckodriver_path_exe = os.path.join(os.path.dirname(__file__), 'geckodriver.exe')
        geckodriver_path = os.path.join(os.path.dirname(__file__), 'geckodriver')
        
        if os.path.exists(geckodriver_path_exe):
            self.geckodriver_path = geckodriver_path_exe
            logger.debug(f"Geckodriver found at {geckodriver_path_exe}")
        elif os.path.exists(geckodriver_path):
            self.geckodriver_path = geckodriver_path
            logger.debug(f"Geckodriver found at {geckodriver_path}")
        else:
            logger.error(f"Geckodriver not found at {geckodriver_path_exe} or {geckodriver_path}")
            raise FileNotFoundError(f"Geckodriver not found at {geckodriver_path_exe} or {geckodriver_path}")

    def browser_init(self):
        """
        Initializes the browser and navigates to the URL
        """
        options = Options()
        # options.headless = True # needs testing
        self.browser = webdriver.Firefox(options=options)
        service = Service(executable_path=self.geckodriver_path)
        self.browser = webdriver.Firefox(service=service, options=options)
        self.browser.get("http://admin:admin@192.168.178.145/menupagex.cgi?nodex2=02005800#02045800")
        self.loading = self.browser.find_element(By.ID, "loading")
        self.loading = self.browser.find_element(By.ID, "loading")
        logger.info("Browser initialized and navigated to the URL")
    
    def quit_browser(self):
        """Quits the browser"""
        if self.browser:
            self.browser.quit()
            logger.info("Browser quit successfully")
        self.browser = None
        self.loading = None

    def get_warmtepomp(self, number: int, click=True):
        """
        Gets the warmtepomp with the given number and optionally clicks on it
        
        Args:
            number (int): The number of the warmtepomp
            click (bool): Whether to click on the warmtepomp
            
        Returns:
            WebElement: The warmtepomp button
        """
        logger.debug(f"Getting warmtepomp {number}")
        WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, "center1")))
        WebDriverWait(self.browser, 20).until(EC.invisibility_of_element(self.loading))
        body = self.browser.find_element(By.ID, "center1")
        boxes = body.find_elements(By.CLASS_NAME, "BOX_OUT")
        wp = None
        for box in boxes:
            if f"Warmtepomp aanvragen {number}" in box.text:
                wp = box
                break
        if wp is None:
            logger.error(f"Warmtepomp {number} not found")
            return None
        wp_button = wp.find_element(By.CLASS_NAME, "VALUE_C_MENU")
        if click:
            wp_button.click()
            logger.debug(f"Clicked warmtepomp {number}")
        return wp_button

    def set_warmtepomp(self, state: WarmtepompSettings) -> bool:
        """
        Sets the warmtepomp to the given state

        Args:
            state (WarmtepompSettings): The state to set the warmtepomp to

        Returns:
            bool: Whether the warmtepomp was set successfully
        """
        if not isinstance(state, WarmtepompSettings):
            logger.error(f"Invalid state: {state}")
            return False

        logger.debug(f"Setting warmtepomp to {state.name}")
        # Select right value
        screen = self.browser.find_element(By.ID, "changer")
        WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, "changeto")))
        dropdown = Select(screen.find_element(By.ID, "changeto"))
        dropdown.select_by_value(state.value)
        # Press OK
        area = self.browser.find_element(By.CLASS_NAME, "ui-dialog")
        button_area = area.find_element(By.CLASS_NAME, "ui-dialog-buttonset")
        buttons = button_area.find_elements(By.CLASS_NAME, "ui-button")
        for button in buttons:
            if button.text == "OK":
                ok = button
                break
        ok.click()
        logger.info(f"Warmtepomp set to {state.name}")
        return True
    
    def get_set_warmptepomp(self, number: int, state: WarmtepompSettings):
        """
        Gets and sets the warmtepomp with the given number to the given state

        Args:
            number (int): The number of the warmtepomp
            state (WarmtepompSettings): The state to set the warmtepomp to
        """
        logger.debug(f"Getting and setting warmtepomp {number} to {state.name}")
        wp = self.get_warmtepomp(number)
        if wp:
            self.set_warmtepomp(state)
        
    def get_set_warmtepompen(self, state: WarmtepompSettings):
        """
        Gets and sets all warmtepompen to the given state

        Args:
            state (WarmtepompSettings): The state to set the warmtepompen to
        """
        logger.info(f"Setting all warmtepompen to {state.name}")
        if self.browser is None:
            self.browser_init()
        self.get_set_warmptepomp(1, state)
        self.get_set_warmptepomp(2, state)
        self.quit_browser()


if __name__ == "__main__":
    browser = Browser()
    try:
        browser.browser_init()
        browser.get_set_warmtepompen(WarmtepompSettings.auto)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        browser.quit_browser()
