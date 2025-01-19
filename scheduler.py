from Browser import Browser
import schedule
from time import sleep


browser = Browser()

def ochtend(): browser.get_set_warmtepompen("auto")

def avond(): browser.get_set_warmtepompen("off")

schedule.every().day.at("06:00").do(ochtend)
schedule.every().day.at("18:00").do(avond)


while True:

    schedule.run_pending()
    sleep(10)