#from re import X
import pyautogui as pag
from time import sleep ,time, strftime, localtime
from random import uniform, randint, choice, normalvariate

def superglass_make(threshold=randint(500,800), Fast=True, Sleeper=True, reg_seaweed=True):

    # Icon locations
    x_Superglass_Max=1611
    x_Superglass_Min=1585
    y_Superglass_Max=557
    y_Superglass_Min=534

    x_Deposit_Max=1394
    x_Deposit_Min=1369
    y_Deposit_Max=745
    y_Deposit_Min=720

    x_Sand_Max=1376
    x_Sand_Min=1341
    y_Sand_Max=682
    y_Sand_Min=651

    x_Seaweed_Max=1303 
    x_Seaweed_Min=1271
    y_Seaweed_Max=681
    y_Seaweed_Min=654

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
        # Molten glass count
    if reg_seaweed: molten_glass_count=threshold*13
    else: molten_glass_count='UNKNOWN'
        # Time of completion
    cast_time = 7.5 # takes approx. 7.5sec to cast superglass make (found using a stop watch after adjusting sleep timers)
    if Sleeper: 
        time_to_complete_sec = cast_time*threshold + \
                                   short_sleep_count*short_sleep_av + \
                                   long_sleep_count*long_sleep_av
        time_of_completion_str = strftime("%H:%M:%S",localtime(time()+time_to_complete_sec))
    else: time_of_completion_str = 'TEST'

    print(f"""Making Molten Glass...
        Threshold: {threshold}
        Approx. motlen glass to be made: {molten_glass_count}
        Approx. time of completion: {time_of_completion_str}
        Expected short sleep(s) (w={short_sleep_weight}): {int(threshold/short_sleep_weight)}
        Expected long sleep(s) (w={long_sleep_weight}): {int(threshold/long_sleep_weight)}
            """)
    print('--------------')


    for i in range(0,threshold):

        print(f'Cast Count: {i}')

        # Open bank and Deposit
        for i in range(1,randint(8,11)):
            x_Deposit=randint(x_Deposit_Min,x_Deposit_Max)
            y_Deposit=randint(y_Deposit_Min,y_Deposit_Max)
            pag.click(x_Deposit,y_Deposit)
            
            if Fast: sleep(uniform(0.09,0.2))
            else: sleep(uniform(0.078,0.35))

        # Get 3x(5 to 7) Sand
        if reg_seaweed:
            sand_amount = 1
        else:
            if 1 == randint(1,10): sand_error=choice([-1,1])
            else:                  sand_error=0
            sand_amount=6+sand_error
            print(f'    Withdrawing {sand_amount*3} buckets of sand.')
        for i in range(sand_amount):
            x_Sand=randint(x_Sand_Min,x_Sand_Max)
            y_Sand=randint(y_Sand_Min,y_Sand_Max)
            pag.click(x_Sand,y_Sand)
            if Fast: sleep(uniform(0.02, 0.2))
            else: sleep(uniform(0.078,0.35))

        # Get 3 Seaweed
        x_Seaweed=randint(x_Seaweed_Min,x_Seaweed_Max)
        y_Seaweed=randint(y_Seaweed_Min,y_Seaweed_Max)
        pag.click(x_Seaweed,y_Seaweed)
        if Fast: sleep(uniform(0.1,0.6))
        else:    sleep(uniform(0.1,1.1))

        # Close Bank
        pag.press('Esc')
        if Fast: sleep(uniform(0.07,0.3))
        else:    sleep(uniform(0.22,0.79))

        # Cast Superglass make
        x_Superglass=randint(x_Superglass_Min,x_Superglass_Max)
        y_Superglass=randint(y_Superglass_Min,y_Superglass_Max)
        pag.click(x_Superglass,y_Superglass)
        if Fast: sleep(uniform(2.8, 4.5))
        else:    sleep(uniform(3.1,4.5))

        # 'Sleep' leftover from old versions (Do not remove. Currently affects Fast=True. Consider implementing a 'sleep check' as with short and long sleeps below)
        if randint(1,10)==1:sleep(uniform(1,8))

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

superglass_make(threshold= int(  63170  / 18) ,
                #threshold=997,
                Fast = True,
                Sleeper = True,
                reg_seaweed = False)

