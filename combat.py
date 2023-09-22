from random import normalvariate, uniform, randint
from time import sleep, time
from bot_builder_and_functions import Bot, BotState, Needle, Haystack
import os
import cv2 as cv

### --------------- CONTROL PANEL --------------- ###
CLIENT_NAME = 'Runelite - Vithala'
RUN_DURATION_HOURS = 5 + normalvariate(.25,0.1)
MONSTER_COLOUR = 'blue'
LOOT_COLOUR = 'purple'
EAT_FOOD = False #TO DO
FOOD = '' #TO Do
DEBUG = False
print('asdasdasd')
def combat(client_name, run_duration_hours, monster_color, loot_colour, eat_food, food, debug):

    bot = Bot(client_name=client_name, debug=debug)
    botstate=BotState()
    bot.state=botstate.INITIALIZING
    time_start=time()
    t_end = time_start + (60 * 60 * run_duration_hours)

    while t_end > time():

        if debug:
            haystack = bot.get_haystack('chat') 
            debug_img, offset = haystack.get_screenshot()
            #bot.find_img(Needle('Images\\how_many_would_you_like_to_cook.jpg'), haystack, threshold=0.1,debug_img=debug_img)
            print('asdasda')
            bot.monster_is_dead()
            print('asa')
            cv.imshow('DEBUG.jpeg', debug_img)
            # Saving a screenshot when 's' is pressed
            if cv.waitKey(1) == ord('s'):
                cv.imwrite(f'DEBUG + {time()}.jpg', debug_img)
                # Ending script when 'q' is pressed (Does not work)
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    break

combat(CLIENT_NAME, RUN_DURATION_HOURS, MONSTER_COLOUR, LOOT_COLOUR, EAT_FOOD, FOOD, DEBUG)
