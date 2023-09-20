from random import normalvariate, uniform
from time import sleep, time
from bot_builder_and_functions import Bot, BotState, Needle, Haystack
import os
import cv2 as cv



### --------------- CONTROL PANEL --------------- ###
CLIENT_NAME = 'Runelite - MouldyAss'
RUN_DURATION_HOURS = 1 + normalvariate(.15,0.1)
WHAT_FISH = ['shrimp', 'anchovies']#['salmon', 'trout']
COOK_FISH = False #TO DO
FISHING_SPOT_COLOUR = 'blue'
FIRE_COLOUR = 'green'
DEBUG = True



### --------------- FIXED SETTINGS FOR ALL BOTS --------------- ###
os.chdir(os.path.dirname(os.path.abspath(__file__)))


### --------------- NEEDLES FOR Fishing --------------- ###

# Fishing Specific
fishing_text        = Needle('Images\\skilling_fishing.jpg')
fishing_not_text    = Needle('Images\\skilling_fishing_not.jpg') #Unused
fish_needles        = [Needle(f'Images\\{fish}.jpg') for fish in WHAT_FISH] 

# Inv Specific
inv_closed          = Needle('Images\\inv_closed.jpg')
inv_open            = Needle('Images\\inv_open.jpg')
inv_full            = Needle('Images\\you_cant_carry_any_more_fish.jpg')

# Chat Speccific
#chat_open_needle    = Needle('Images\\press_enter_to_chat.jpg')

# Bank Specific
# None

if COOK_FISH: #UNTESTED
    cooked_fish = ['cooked_'+fish for fish in WHAT_FISH]
    cooked_fish_needles = [Needle(x) for x in cooked_fish]



### --------------- Fishing Function --------------- ###
def fishing(client_name, run_duration_hours, fishing_spot_colour, debug):

    bot = Bot(client_name=client_name, debug=debug)
    botstate=BotState()
    global COOK_FISH

    time_start=time()
    t_end = time_start + (60 * 60 * run_duration_hours)

    bot.state=botstate.INITIALIZING

    while t_end > time():

        if DEBUG:
            #bot.show_windows()

            #screenshot, offset = bot.get_haystack('client').get_screenshot()
            haystack = bot.get_haystack('skilling')
            debug_img, offset = haystack.get_screenshot()
            print(bot.skilling_check('fishing', config='--psm 6'))
            #inv_haystack = bot.get_haystack('inv')
            #haystack_img, offset = haystack.get_screenshot()
            # Show screenshots  
            #inv_open_coords=bot.find_img(inv_open, haystack, 0.8, debug_mode='rectangles',debug_img=debug_img)
            #inv_closed_coords=bot.find_img(inv_closed, haystack, 0.8, debug_mode='rectangles',debug_img=debug_img)
            #fishing_text_coords=bot.find_img(fishing_text, haystack, 0.6, debug_mode='rectangles',debug_img=debug_img)
            #fishing_text_not_coords=bot.find_img(fishing_not_text, haystack, 0.6, debug_mode='rectangles',debug_img=debug_img)
            #fish_needles_coords=bot.find_img(fish_needles[0], haystack, 0.975, debug_mode='rectangles',debug_img=debug_img)
            #fish_needles_coords=bot.find_img(fish_needles[1], haystack, 0.975, debug_mode='rectangles',debug_img=debug_img)
            #fishing_spot_contours_coords=bot.find_contours(fishing_spot_colour, "client", debug_img=debug_img)
            #inv_full_coords=bot.find_img(inv_full, haystack, 0.8, debug_mode='rectangles',debug_img=debug_img)
            #chat_open_coords=bot.find_img(chat_open_needle, haystack, 0.8, debug_mode='rectangles',debug_img=debug_img)
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
            bot.set_view()
            bot.open_inv()
            bot.close_chat()
            bot.state=botstate.CHECKING_INV

        # 2. Checking Inventory
        if bot.state==botstate.CHECKING_INV:
            print("CHECKING_INV")
            a = bot.count_fish(fish_needles)
            b = bot.count_clues(None)
            if a+b < 27: # space is avaliable in inv
                bot.state=botstate.FISHING
            else: # a+b => 26
                if COOK_FISH == False:
                    bot.state=botstate.DROPPING_FISH
                else: 
                    bot.state=botstate.COOKING
                    print('Cooking fish is yet to be implemented')

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
            bot.drop_fish(fish_needles) #TO DO: Make a more natural dropping pattern. E.g left-right-right-left, maybe add randon check to miss one and go back.
            bot.state=botstate.FISHING

        if bot.state==botstate.COOKING:
            print('COOKING')
            continue

fishing(CLIENT_NAME, RUN_DURATION_HOURS, FISHING_SPOT_COLOUR, DEBUG)
