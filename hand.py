import pyautogui
from math import sqrt
from random import randint, normalvariate
from time import sleep

class Hand:

    def __init__(self): 

        self.prev_coord = None
        pass
        

    def click(self, coord, side='left', randomizeCoord = True, move=False, speed=2000):
        #coord = Coordinates
        #side = which mouse botton to click: left, riht, middle.
        #randomizeCoord adds a bit of randomization to the final coordinates
        #move determines if the mouse should move to its new location. move=False simply clicks the final coordinates
        #speed=2000 -> 2000px per 1sec if move=True
        
        x_coord=coord[0]
        y_coord=coord[1]

        if randomizeCoord:

            w=13 #these w and h values are just guesses. Would be better if you were passed the img's actual w and h data.
            h=13
            x_sd=w/3
            y_sd=h/3

            x_coord=int(normalvariate(x_coord,x_sd))
            y_coord=int(normalvariate(y_coord,y_sd))
        
        dur=0
        if move:
            #Calcualte duration of mouse movement from speed
            cur_mouse_pos = pyautogui.position()
            x_coord=coord[0]
            y_coord=coord[1]
            x_cur = cur_mouse_pos[0]
            y_cur = cur_mouse_pos[1]
            dis = sqrt((x_coord-x_cur)**2 + (y_coord-y_cur)**2)

            dur=dis/speed + 0.01*randint(-5,5)

        pyautogui.click(x_coord, y_coord, button=side, duration=dur)

    @staticmethod
    def write(key):
        if key == 'esc' or key == 'space': 
            pyautogui.keyDown(key)
            sleep(normalvariate(0.06,0.011))
            pyautogui.keyUp(key)
        else:   
            for char in key:
                pyautogui.write(key)
                sleep(normalvariate(0.06,0.011))
            