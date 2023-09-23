import woodcutter
import fishing
from random import normalvariate, uniform, randint
from time import sleep, time

import subprocess
import os
from threading import Thread

os.chdir(os.path.dirname(os.path.abspath(__file__)))


Dalakane_control_panel = (  'Runelite - Dalakane',      
                            5 + normalvariate(.25,0.1), 
                            'oak_logs',                 
                            'blue',                       
                            'green',                    
                            False,                      
                            True,                       
                            True,                     
                            False                       
                        )

Vithala_control_panel = (   'Runelite - Vithala',
                            3 + normalvariate(.15,0.1),
                            ['trout', 'salmon'],
                            'blue',
                            False,
                            'green',
                            False
                        )

Kinjor_control_panel = (  'Runelite - Kinjor',      
                            5 + normalvariate(.25,0.1), 
                            'logs',                 
                            'blue',                       
                            'green',                    
                            False,                      
                            False,                       
                            False,                     
                            False                       
                        )

# woodcutter(client_name, 
    # run_duration_hours, 
    # what_logs, 
    # tree_spot_colour, 
    # bank_colour, 
    # light_fires=False, 
    # bank_logs=False, 
    # axe_in_inv=False, 
    # debug=False)

# fishing(client_name, 
    # run_duration_hours, 
    # what_fish, 
    # fishing_spot_colour, 
    # cook_fish, 
    # cooking_colour, 
    # debug)

t1=Thread(target=woodcutter.woodcutter, args=Dalakane_control_panel)
t2=Thread(target=fishing.fishing, args=Vithala_control_panel)
t3=Thread(target=woodcutter.woodcutter, args=Kinjor_control_panel)

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()

"""
def start_bot(filename):
    subprocess.run(filename, shell=True)

threads_paused = False

filenames = ["fishing.py","woodcutter.py"]

#t=Thread(target=start_bot, args=["woodcutter.py",])
#t.start()
threads = []

for filename in filenames:
    threads.append(Thread(target=start_bot, args=[filename,]))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
"""