from random import normalvariate, uniform, randint
from time import sleep, time
from bot_builder_and_functions import Bot, BotState, Needle, Haystack
import os
import cv2 as cv
from threading import Lock



### --------------- CONTROL PANEL --------------- ###
CLIENT_NAME = 'Runelite - Vithala'
RUN_DURATION_HOURS = 2 + normalvariate(.25,0.1)
HIGH_ALCH_COLOUR = 'green' #GREEN IS CURRENTLY THE ONLY FUNCTIONING COLOUR
DEBUG = False

### --------------- Fishing Function --------------- ###
def high_alch(client_name, run_duration_hours, high_alch_colour, debug=False):

    bot = Bot(client_name=client_name, debug=debug)
    botstate=BotState()

    time_start=time()
    t_end = time_start + (60 * 60 * run_duration_hours)

    empty_HA_needle = Needle(f'Images\\empty_HA.jpg')
    empty_nature_rune_needle = Needle(f'Images\\empty_nature_runes.jpg')

    bot.state=botstate.INITIALIZING

    while t_end > time():

        if DEBUG:
            #bot.show_windows()

            #screenshot, offset = bot.get_haystack('client').get_screenshot()
            #haystack = bot.get_haystack('bank')
            #debug_img, offset = haystack.get_screenshot()
            debug_img=bot.skilling_check('woodcutting')
            #print(bot.skilling_check('fishing', config='--psm 1'))
            cv.imshow('DEBUG.jpeg', debug_img)
            # Saving a screenshot when 's' is pressed
            if cv.waitKey(1) == ord('s'):
                cv.imwrite(f'DEBUG + {time()}.jpg', debug_img)
            # Ending script when 'q' is pressed (Does not work)
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                break

        # 1. Initilising
        if bot.state==botstate.INITIALIZING:
            print("INITIALIZING")
            #click north and "up" arrow key (Add a scroll out?)
            #bot.set_view()
            bot.open_inv()
            #bot.close_chat()
            coord = bot.find_contours(high_alch_colour,region='inv',key='max_area')
            bot.state=botstate.HIGH_ALCHING

        # 2. Checking Inventory
        if bot.state==botstate.HIGH_ALCHING:
            print("HIGH_ALCHING")
            bot.click(coord,randomizeCoord=False)
             # <- Click Spell
            sleep(uniform(0.1,0.4)+uniform(0.02,1)+normalvariate(0.05,0.1))
            bot.click(coord, randomizeCoord=False) 
            sleep(uniform(1,3.5)+uniform(0.13,1.1)+normalvariate(0.04,0.1))

            # random click because why not
            if randint(0,3)==1: bot.click(coord,randomizeCoord=False)
            bot.shortSleep(40)
            if randint(0,9)==1: bot.click(coord,randomizeCoord=False)
            bot.shortSleep(60)            
            if randint(0,25)==1: bot.click(coord,randomizeCoord=False)
            bot.shortSleep(150)

            if bot.find_img(empty_HA_needle, bot.get_haystack('inv')) or bot.find_img(empty_nature_rune_needle, bot.get_haystack('inv'), threshold=0.9):
                bot.state=botstate.STOPPING
            bot.longSleep(300)

        if bot.state==botstate.STOPPING:
            print("STOPPING")
            for _ in range(randint(0,4)):
                bot.click(coord,randomizeCoord=False)
                # <- Click Spell
                sleep(uniform(0.1,0.4)+uniform(0.01,1)+normalvariate(0.05,0.1))
                bot.click(coord, randomizeCoord=False) 
                sleep(uniform(1,3.5)+uniform(0.1,1)+normalvariate(0.04,0.1))
            return
               
high_alch(CLIENT_NAME, RUN_DURATION_HOURS, HIGH_ALCH_COLOUR, DEBUG)
