# from handler import Browser
# import schedule
# from time import sleep
# from config import WarmtepompSettings as WS


# browser = Browser()

# def ochtend(): browser.get_set_warmtepompen(WS.auto)

# def avond(): browser.get_set_warmtepompen(WS.off)

# schedule.every().day.at("06:00").do(ochtend)
# schedule.every().day.at("18:00").do(avond)


# while True:

#     schedule.run_pending()
#     sleep(10)
