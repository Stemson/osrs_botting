from random import uniform, randint, normalvariate
from time import sleep   

# Random sleeps

class Sleep:

    def __init__(self):
        pass

    def clickSleeper(task):
        if task=='open_bank_or_deposit': sleep(uniform(0.09,0.2))
        if task=='widthdraw':            sleep(uniform(0.02, 0.2))
        if task=='close_bank':           sleep(uniform(0.07,0.3))
        if task=='spam':                 sleep(normalvariate(0.06,0.011)+uniform(0.9, 2))
        if task=='make':                 sleep(uniform(16.7,17.3)+uniform(0.1,1.3))
        if task=='inv_item':             sleep(uniform(0.11,0.3))

    def shortSleep(short_sleep_weight=12, short_sleep_av=3.5, short_sleep_sd=uniform(0.8,1.2),debug_mode=True):
        short_sleep_check = randint(1,short_sleep_weight) 
        if debug_mode: print(f'    Short sleep check: {short_sleep_check}')   
        if short_sleep_check == 1:                             
            short_sleep_time=normalvariate(short_sleep_av,short_sleep_sd)
            print(f'    Sleeping for: {round(short_sleep_time,2)} sec')
            sleep(short_sleep_time)
            # Can remove sleep check variable if happy to lose for debugging purposes
            # if randint(0,long_sleep_weight) == 1: 
            #   short_sleep_time=normalvariate(short_sleep_av,short_sleep_sd)
            #   print(f'    Sleeping for: {round(short_sleep_time,2)} sec')
            #   sleep(short_sleep_time)

    def longSleep(long_sleep_weight=150, long_sleep_av=180, long_sleep_sd=uniform(40,50),debug_mode=True):
        long_sleep_check = randint(1,long_sleep_weight) 
        if debug_mode: print(f'    Long sleep check: {long_sleep_check}')   
        if long_sleep_check == 1:                       
            long_sleep_time=normalvariate(long_sleep_av,long_sleep_sd)
            print(f'    Sleeping for: {round(long_sleep_time,2)} sec')
            sleep(long_sleep_time)


"""
class Sleep:

    # constants
    
    # properties

    # constructor
    def __init__(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def sleep(self):
        pass
"""