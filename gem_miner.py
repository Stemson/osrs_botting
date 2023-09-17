from random import normalvariate, uniform
from time import sleep, time
from bot_builder_and_functions import Bot, BotState, Needle, Haystack
import os
import cv2 as cv



### --------------- CONTROL PANEL --------------- ###
CLIENT_NAME = 'Runelite - 10072'
RUN_DURATION_HOURS = 0.9 + normalvariate(.15,0.1)
WHAT_GEMS = ['diamond', 'red_topaz',  'ruby', 'emerald', 'sapphire'] # ['opal', 'jade'] opals, jade, and diamond are seen as the same by open cv
GEM_MINE_COLOUR = 'blue'
BANK_COLOUR = 'green'
RESET_COLOUR = 'green'
DEBUG = False
#DEBUG = False




### --------------- FIXED SETTINGS FOR ALL BOTS --------------- ###
os.chdir(os.path.dirname(os.path.abspath(__file__)))


### --------------- NEEDLES FOR Fishing --------------- ###

# Mining Specific
mining_text        = Needle('Images\\skilling_mining.jpg')
mining_not_text    = Needle('Images\\skilling_mining_not.jpg') #Unused
gem_needles        = [Needle(f'Images\\{gem}.jpg') for gem in WHAT_GEMS] 

# Inv Specific
inv_closed          = Needle('Images\\inv_closed.jpg')
inv_open            = Needle('Images\\inv_open.jpg')
inv_full            = Needle('Images\\you_cant_carry_any_more_gems.jpg')

# Chat Speccific
# None

# Bank Specific
# None

# Needles for debugging (avaliable in bot_builder)
all_icon_unselected_BIG =   Needle('Images\\all_icon_unselected_BIG.jpg')
all_icon_selected_BIG =     Needle('Images\\all_icon_selected_BIG.jpg')
deposit_box_title=     Needle('Images\\deposit_box_title.jpg')
full_special_attack = Needle('Images\\full_special_attack.jpg')
deposit =               Needle('Images\\deposit.jpg')


### --------------- Gem Mining Function --------------- ###
def gem_miner(client_name, run_duration_hours, gem_mine_colour, bank_colour, reset_colour, debug):


    bot = Bot(client_name=client_name, debug=debug)
    botstate=BotState()
    
    all_is_selected=False

    time_start=time()
    t_end = time_start + (60 * 60 * run_duration_hours)

    bot.state=botstate.INITIALIZING

    while t_end > time():

        if DEBUG:
            #bot.show_windows()
            #screenshot, offset = bot.get_haystack('client').get_screenshot()
            region='attack_power'
            #haystack = bot.get_haystack('client')
            haystack = bot.get_haystack(region)  
            #haystack = bot.get_haystack('prayer')  
            #haystack = bot.get_haystack('stamina')  
            #haystack = bot.get_haystack('attack_power')    
            #haystack = bot.get_haystack('skilling')
            debug_img, offset = haystack.get_screenshot()
            print(bot.read_stat(region))
            bot.click_attack_power(100)
            bot.skilling_check('mining') #debugging for skill check is within the function 
            #inv_haystack = bot.get_haystack('inv')
            #haystack_img, offset = haystack.get_screenshot()
            # Show screenshots  
            #test_contours=bot.find_contours('blue','client',debug_img=debug_img, key='dist')
            #test_contours=bot.find_contours('green','client',debug_img=debug_img, ignore_region='inv')
            #bot.count_gems(gem_needles)
            #inv_gem_coords=bot.find_img(gem_needles[0], haystack, 0.8, debug_mode='rectangles',debug_img=debug_img)
            #desat_gem=cv.imread(gem_needles[0].needle_img,0)
            #for gem_needle in gem_needles:
            #    inv_gem_coords=bot.find_img(gem_needle, haystack, 0.8, debug_mode='rectangles',debug_img=debug_img)
            #mining_text_coords=bot.skilling_check('mining')
            #mining_text_coords=bot.skilling_check('mining')
            #a=bot.find_img(full_special_attack, haystack, 0.85, debug_mode='rectangles',debug_img=debug_img)
            #a=bot.find_img(all_icon_unselected_BIG, haystack, 0.85, debug_mode='rectangles',debug_img=debug_img)
            #a=bot.find_img(deposit_box_title, haystack, 0.85, debug_mode='rectangles',debug_img=debug_img)
            #a=bot.find_img(all_icon_selected_BIG, haystack, 0.85, debug_mode='rectangles',debug_img=debug_img)  
            #a=bot.find_img(deposit, haystack, 0.85, debug_mode='rectangles',debug_img=debug_img)            
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
        if bot.state == botstate.INITIALIZING:
            print("INITIALIZING")
            #click north and "up" arrow key (Add a scroll out?)
            bot.set_view()
            bot.open_inv()
            bot.close_chat()
            bot.state=botstate.CHECKING_INV

        # 2. Checking Inv
        if bot.state==botstate.CHECKING_INV:
            print("CHECKING_INV")
            if bot.count_gems(gem_needles) < 28: # space is avaliable in inv
                bot.state=botstate.MINING
            else: # count => 28
                bot.state=botstate.DEPOSITING

        # 3. Mining
        if bot.state==botstate.MINING:
            print("MINING")
            if not bot.skilling_check('mining'):
                gem_spot=bot.find_contours(gem_mine_colour, "client", ignore_region='inv')
                bot.click(gem_spot)
                bot.click(gem_spot)
                sleep(uniform(1.5,3) + normalvariate(0.9,0.12)) # Wait time while character moves to fishing spot
                bot.shortSleep()
            bot.state=botstate.CHECKING_INV

        # 4. Depositing
        if bot.state==botstate.DEPOSITING:
            if bot.despoit_box_is_open(): #deposit boxes have a bigger icon
                #bot.check_all_is_selected(big=True) # Not needed when selecting 'deposit'
                bot.deposit()
                bot.close_bank()
                bot.longSleep()
                bot.click_attack_power(100)
                bot.state=botstate.MINING
            else: #Need to find deposit box
                bank_spot=bot.find_contours(bank_colour,'client',key='min_area', ignore_region='inv')
                if bank_spot: # Would using .size>0 work?
                    bot.click(bank_spot)
                    bot.click(bank_spot)
                    sleep(uniform(1.2,3) + normalvariate(0.5,0.12))
                else:
                    print('No "bank colour" has been identified')
                #else: # No bank contours have been found
                #    reset_spot=bot.find_contours(reset_colour,'client')
                #    bot.click(reset_spot)
                #    sleep(uniform(1,8) + normalvariate(0.5,0.12))



gem_miner(CLIENT_NAME, RUN_DURATION_HOURS, GEM_MINE_COLOUR, BANK_COLOUR, RESET_COLOUR, DEBUG)