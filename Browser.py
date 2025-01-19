from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


class Browser():
    
    def __init__(self):
        self.browser = None
        self.loading = None

    def browser_init(self):
        options = Options()
        # options.headless = True # needs testing
        self.browser = webdriver.Firefox(options=options)
        self.browser.get("admin:admin@192.168.178.145/menupagex.cgi?nodex2=02005800#02045800")
        self.loading = self.browser.find_element(By.ID, "loading")
        
    
    def quit_browser(self):
        self.browser.quit()
        self.browser = None
        self.loading = None

    def get_warmtepomp(self, number, click = True):
        WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, "center1")))
        WebDriverWait(self.browser, 20).until(EC.invisibility_of_element(self.loading))
        body = self.browser.find_element(By.ID, "center1")
        boxes = body.find_elements(By.CLASS_NAME, "BOX_OUT")
        for box in boxes:
            if "Warmtepomp aanvragen {}".format(number) in box.text:
                wp = box
                break
        wp_button = wp.find_element(By.CLASS_NAME, "VALUE_C_MENU")
        if click: wp_button.click()
        return wp_button

    def set_warmtepomp(self, wp, state):
        if state != "auto" and state != "off" and state != "on":
            print("invalid state")
            return False
        
        if state == "off": value = "0"
        elif state == "on": value = "1"
        elif state == "auto": value = "2"
        #select right value
        screen = self.browser.find_element(By.ID, "changer")
        WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, "changeto")))
        dropdown = Select(screen.find_element(By.ID, "changeto"))
        dropdown.select_by_value(value)
        #press ok
        area = self.browser.find_element(By.CLASS_NAME, "ui-dialog")
        button_area = area.find_element(By.CLASS_NAME, "ui-dialog-buttonset")
        buttons = button_area.find_elements(By.CLASS_NAME, "ui-button")
        for button in buttons:
            if button.text == "OK":
                ok = button
                break
        ok.click()
        return True
    
    def get_set_warmptepomp(self, number, state):
        wp = self.get_warmtepomp(number)
        self.set_warmtepomp(wp, state)
        
    def get_set_warmtepompen(self, state):
        if self.browser == None: self.browser_init()
        self.get_set_warmptepomp(1, state)
        self.get_set_warmptepomp(2, state)
        self.quit_browser()



    
        

# browser = Browser()
# browser.browser_init()
# browser.get_set_warmtepompen("auto")
# browser.quit_browser()



