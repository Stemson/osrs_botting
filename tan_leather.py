from turtle import Turtle
import pyautogui as pag
from time import sleep ,time, strftime, localtime
from random import uniform, randint, choice, normalvariate

def Tan_Lether_make(threshold=randint(500,800), Fast=True, Sleeper=True, reg_seaweed=True):

    # Icon locations
    x_first_spell_max=1611
    x_first_spell_min=1585
    y_first_spell_max=557
    y_first_spell_min=534

    x_deposit_max=1394
    x_deposit_min=1369
    y_deposit_max=745
    y_deposit_min=720

    x_bank_item_max=1376
    x_bank_item_min=1341
    y_bank_item_max=682
    y_bank_item_min=651

    # Intilixing sleep settings
    short_sleep_weight=12 # 1 in <weight> casts will have a short sleep
    short_sleep_av=3.5
    short_sleep_sd=uniform(0.8,1.2)
    short_sleep_count=int(threshold/short_sleep_weight)
    long_sleep_weight=150 # 1 in <weight> casts will have a long sleep
    long_sleep_av=180
    long_sleep_sd=uniform(40,50)
    long_sleep_count=int(threshold/long_sleep_weight)

    # Printing initialiation message
        # csat count
    leather_count=threshold*5*5
        # Time of completion
    cast_time = 12.5 # takes approx. 7.5sec to cast Tan_Lether make (found using a stop watch after adjusting sleep timers)
    if Sleeper: 
        time_to_complete_sec = cast_time*threshold + \
                                   short_sleep_count*short_sleep_av + \
                                   long_sleep_count*long_sleep_av
        time_of_completion_str = strftime("%H:%M:%S",localtime(time()+time_to_complete_sec))
    else: time_of_completion_str = 'TEST'

    print(f"""Tanning Leather...
        Threshold: {threshold}
        Leather to be made: {leather_count}
        Astral runes needed: {threshold*2*5}
        Nature runes needed: {threshold*5}
        Approx. time of completion: {time_of_completion_str}
        Expected short sleep(s) (w={short_sleep_weight}): {int(threshold/short_sleep_weight)}
        Expected long sleep(s) (w={long_sleep_weight}): {int(threshold/long_sleep_weight)}
            """)
    print('--------------')


    for i in range(0,threshold):

        print(f'Cast Count: {i} / {threshold}')

        # 1. Open bank and Deposit
        for i in range(1,randint(8,11)):
            x_Deposit=randint(x_deposit_min,x_deposit_max)
            y_Deposit=randint(y_deposit_min,y_deposit_max)
            pag.click(x_Deposit,y_Deposit)
            if Fast: sleep(uniform(0.09,0.2))
            else:    sleep(uniform(0.078,0.35))

        # 2. Withdraw dragonhide
        x_bank_item=randint(x_bank_item_min,x_bank_item_max)
        y_bank_item=randint(y_bank_item_min,y_bank_item_max)
        pag.click(x_bank_item,y_bank_item)
        if Fast: sleep(uniform(0.02, 0.2))
        else:    sleep(uniform(0.078,0.35))

        # Close Bank
        pag.press('Esc')
        if Fast: sleep(uniform(0.07,0.3))
        else:    sleep(uniform(0.22,0.79))

        # Cast Tan_Lether make
        cast_click_count=randint(35,52)
        print(f'    Clicking tan leather {cast_click_count} times.')
        x_first_spell_av=(x_first_spell_max+x_first_spell_min)/2
        x_first_spell_sd=(x_first_spell_av-x_first_spell_min)/3
        y_first_spell_av=(y_first_spell_max+y_first_spell_min)/2
        y_first_spell_sd=(y_first_spell_av-y_first_spell_min)/3
        for i in range(cast_click_count):
            x_tan_leather=int(normalvariate(x_first_spell_av,x_first_spell_sd))
            y_tan_leather=int(normalvariate(y_first_spell_av,y_first_spell_sd))
            #_tan_leather=randint(x_first_spell_min,x_first_spell_max)
            #y_tan_leather=randint(y_first_spell_min,y_first_spell_max)
            pag.click(x_tan_leather,y_tan_leather)
            sleep(normalvariate(0.06,0.011))
        if Fast: sleep(uniform(0.9, 2))
        else:    sleep(uniform(3.1,4.5))

        # 'Sleep' leftover from old versions (Do not remove. Currently affects Fast=True. Consider implementing a 'sleep check' as with short and long sleeps below)
        #if randint(1,10)==1:sleep(uniform(1,8))

        # Random sleeps
        if Sleeper:
            # Short sleep
            short_sleep_check = randint(1,short_sleep_weight) #
            print(f'    Short sleep check: {short_sleep_check}')   # Will remove sleep_check variable on day. 
            if short_sleep_check == 1:                       # if randint(0,long_sleep_weight) == 1: ...
                short_sleep_time=normalvariate(short_sleep_av,short_sleep_sd)
                print(f'    Sleeping for: {round(short_sleep_time,2)} sec')
                sleep(short_sleep_time)

            # Long sleep
            long_sleep_check = randint(1,long_sleep_weight) #
            print(f'    Long sleep check: {long_sleep_check}')   # Will remove sleep_check variable on day. 
            if long_sleep_check == 1:                       # if randint(0,long_sleep_weight) == 1: ...
                long_sleep_time=normalvariate(long_sleep_av,long_sleep_sd)
                print(f'    Sleeping for: {round(long_sleep_time,2)} sec')
                sleep(long_sleep_time)

        print('--------------')
    print(strftime("%H:%M:%S",localtime(time())))

Tan_Lether_make(#threshold=randint(100,200),
                threshold=int(  10050 /25),
                Fast = True,
                Sleeper = True)

