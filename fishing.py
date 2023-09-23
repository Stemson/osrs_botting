from random import normalvariate, uniform
from time import sleep, time
from bot_builder_and_functions import Bot, BotState, Needle, Haystack
import os
import cv2 as cv
from threading import Lock

### --------------- CONTROL PANEL --------------- ###
CLIENT_NAME = 'Runelite - Vithala'
RUN_DURATION_HOURS = 3 + normalvariate(.15,0.1)
WHAT_FISH = ['trout', 'salmon']  # ['shrimp', 'anchovies']
COOK_FISH = False 
FISHING_SPOT_COLOUR = 'blue'
COOKING_COLOUR = 'green'
DEBUG = False


### --------------- FIXED SETTINGS FOR ALL BOTS --------------- ###
os.chdir(os.path.dirname(os.path.abspath(__file__)))



### --------------- Fishing Function --------------- ###
def fishing(client_name, run_duration_hours, what_fish, fishing_spot_colour, cook_fish, cooking_colour, debug):

    bot = Bot(client_name=client_name, debug=debug)
    botstate=BotState()
    bot.state=botstate.INITIALIZING
    time_start=time()
    t_end = time_start + (60 * 60 * run_duration_hours)

    #Fishing specific needles
    fish_needles = [Needle(f'Images\\{fish}.jpg') for fish in what_fish] 
    if cook_fish: 
        fish_cooked_needles = [Needle(f'Images\\{fish}_cooked.jpg') for fish in what_fish] + [Needle(f'Images\\{fish}_burnt.jpg') for fish in what_fish] 
        if 'trout' and 'salmon' in what_fish:
            fish_cooked_needles.pop() #Salmon and trout have the same burnt fish icon, if both are present one must be removed to avoid double counting.
    else:         fish_cooked_needles = []
    fish_all_needles = fish_needles+fish_cooked_needles

    inv_full_count = 28
    if   'trout'  in what_fish: inv_full_count -= 2
    elif 'shrimp' in what_fish: inv_full_count -= 1
    elif True: pass # ADD NEW FISH HERE

    while t_end > time():

        if DEBUG:
            haystack = bot.get_haystack('client') 
            debug_img, offset = haystack.get_screenshot()
            #bot.find_img(Needle('Images\\how_many_would_you_like_to_cook.jpg'), haystack, threshold=0.1,debug_img=debug_img)
            #bot.read_chat('skilling')
            bot.find_contours('blue', debug_img=debug_img)
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
            bot.state=botstate.CHECKING_INV

        # 2. Checking Inventory
        if bot.state==botstate.CHECKING_INV:
            print("CHECKING_INV")
            a = bot.count_fish(fish_all_needles)
            b = bot.count_clues(None)
            if a+b < inv_full_count: # space is avaliable in inv
                bot.state=botstate.FISHING
            else: # a+b => inv_full_count
                if cook_fish == False:
                    bot.state=botstate.DROPPING_FISH
                else: 
                    bot.state=botstate.COOKING

        # 3. Fnding and Catching fish
        if bot.state==botstate.FISHING:
            print("FISHING")
            if not bot.skilling_check('fishing'):
                fishing_spot=bot.find_contours(fishing_spot_colour, "client")
                bot.click(fishing_spot)
                bot.click(fishing_spot)
                sleep(uniform(3,8)+uniform(-2,5) + normalvariate(0.5,0.12)) # Wait time while character moves to fishing spot
                bot.shortSleep()
                bot.longSleep()
            sleep(uniform(2,4))
            bot.state=botstate.CHECKING_INV


        # 4. Dropping fish
        if bot.state==botstate.DROPPING_FISH:
            print("DROPPING_FISH")
            bot.drop_fish(fish_all_needles) #TO DO: Make a more natural dropping pattern. E.g left-right-right-left, maybe add randon check to miss one and go back.
            bot.state=botstate.FISHING

        if bot.state==botstate.COOKING:
            print('COOKING')
            if bot.cooking_panel_is_open():
                bot.start_cooking() # just a 'press space' function
                bot.state=botstate.COOKING
            elif bot.skilling_check('cooking'): 
                sleep(uniform(2,4))
                pass
            else:
                cooked_fish=bot.count_fish(fish_cooked_needles)
                if cooked_fish<inv_full_count:
                    cook_spot=bot.find_contours(cooking_colour,'client',key='dist', ignore_region='inv')
                    if cook_spot: 
                        bot.click(cook_spot)
                        bot.click(cook_spot)
                        sleep(uniform(1.2,3) + normalvariate(0.5,0.12))
                    else:
                        print('No "cooking colour" has been identified')
                else:
                    bot.state=botstate.DROPPING_FISH

#fishing(CLIENT_NAME, RUN_DURATION_HOURS, WHAT_FISH, FISHING_SPOT_COLOUR, COOK_FISH, COOKING_COLOUR, DEBUG)
