import os
import pyautogui
from numpy import add, array, fromstring, ascontiguousarray, where, append
from math import sqrt
from random import uniform, randint, normalvariate, randrange
from time import sleep
import cv2 as cv
import win32gui
import win32ui
import win32con
from PIL import Image, ImageGrab

import pytesseract
#NOTE to install pytesseract for image_to_text functions refer to https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


os.chdir(os.path.dirname(os.path.abspath(__file__)))


### --------------- Needle and Haystack Classes Start --------------- ###
class Needle:

    # class properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None
    path = None

    # constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):

        self.path = needle_img_path
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        self.method=method
        pass

class Haystack:

    # class properties
    w = 0
    h = 0
    hwnd = None
    left=0
    top=0
    right=0
    bottom=0
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    rect = []
    cropped_region=None

    # constructor
    def __init__(self, window_name=None, cropped_region=array([])):
        self.cropped_region=cropped_region
        # find the handle for the window we want to capture   ### DEBUG CHECK: GOOD
        if window_name==None: self.hand = win32gui.GetDesktopWindow()
        else:                 self.hwnd = win32gui.FindWindow(None, window_name)
        
        #Leftover code - Delete?
        #if not self.hwnd:
        #    raise Exception(f'Window not found: {window_name}')

        # get the window size
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.hwnd)
        self.w = self.right - self.left
        self.h = self.bottom - self.top           

        # account for the window border and titlebar and cut them off
        if self.cropped_region.size==0:  # All cropped regions should be from the top right of the client region
            border_pixels = 4
            titlebar_pixels = 27
            plugin_bar = 40
            self.w = self.w - (border_pixels * 2) - plugin_bar
            self.h = self.h - titlebar_pixels - border_pixels
            self.cropped_x = border_pixels
            self.cropped_y = titlebar_pixels

            # set the cropped coordinates offset so we can translate screenshot
            # coordinates into actual screen coordinates
            self.offset_x = self.left + self.cropped_x
            self.offset_y = self.top + self.cropped_y
            #self.cropped_region = [self.offset_x, self.offset_y, self.w, self.h]

        else: #cropped_region = [x,y,w, h]
            #self.offset_x, self.offset_y, self.w, self.h = self.cropped_region
            self.offset_x = self.cropped_region[0]
            self.offset_y = self.cropped_region[1]
            self.w = self.cropped_region[2]
            self.h = self.cropped_region[3]



    def get_screenshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        if self.cropped_region.size==0:
            cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
        else:
            cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.offset_x-self.left, self.offset_y-self.top), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = ascontiguousarray(img)

        return img, [self.offset_x, self.offset_y]

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    
    def list_window_names(self):
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)

### --------------- Needle and Haystack Classes End --------------- ###

### --------------- BUILDING BOT --------------- ###

class BotState: 
    #Constants
    INITIALIZING = 0
    OPENING_BANK = 1
    WITHRAWING = 2
    MAKINMG = 3
    DEPOSITING = 4
    DROPPING_INV = 5
    FISHING = 6
    CHECKING_INV = 7
    DROPPING_FISH = 8
    MINING = 9
    WOODCUTTING = 10
    DROPPING_LOGS = 11
    LIGHTING_FIRES = 12
    COOKING = 13


class Bot(Haystack,Needle):
    # constants
    OFFSET=[0,0]                   # This surely isnt right, OFFSET will need to updated to be 
    THRESHOLD = 0.9                # Consider making individual thresholds for needles
    DEBUG_MODE = 'rectangles'
    RANDOMIZE_COORDS=True
    BANK_OFFSET_INITIAL = [34,3]
    BANK_SIZE_INITIAL= [484,331] # [x,y,w,h] #TO DO: Update abnk region to be dynamic (similar to inv, chat, and skilling)
    GE_REGION = []
    INV_REGION = [580, 194, 172, 250] #Change to dimensions and offset_from_BR
    INV_SIZE = [250,370]
    INV_OFFSET_FROM_BR = [-1*x for x in INV_SIZE] #[-200,-344]  #ASSUMPTION: Both menu bars are stacked. i.e. game window wisth is less than 990 pixels. 
    CHAT_SIZE = [520,170]
    CHAT_OFFSET_FROM_BL = [0,-CHAT_SIZE[1]] #[0,-166]
    CHAT_ALL_OFFSET_FROM_BL = [32,-15]
    SKILLING_SIZE = [123,180]#52
    SKILLING_OFFSET_FROM_TL = [5,4] #[0,0]
    COMPASS_OFFSET_FROM_TR = [-158, 21]
    DESPOSIT_BOX_OFFSET_INITIAL = [50,30]
    DESPOSIT_BOX_OFFSET_SIZE = [455,285]
    HEALTH_OFFSET_FROM_TR=[-205,57]
    HEALTH_SIZE=[25,20]
    PRAYER_OFFSET_FROM_TR=[-205,92]
    PRAYER_SIZE=[25,20]
    STAMINA_OFFSET_FROM_TR=[-200,124]
    STAMINA_SIZE=[28,20]
    ATTACK_POWER_OFFSET_FROM_TR=[-172,148]
    ATTACK_POWER_SIZE=[25,23]
    MINIMAP_OFFSET_FROM_TR=[]
    MINIMAP_SIZE=[]
    #
    CLIENT_SIZE_INTIAL = [765,500]

    # properties
    client_haystack=None
    inv_haystack=None
    chat_haystack=None
    skilling_haystack=None
    deposit_box_region_haystack=None
    top_left=[]
    top_right=[]
    bottom_left=[]
    bottom_right=[]
    centre=[]
    inv_region=[]
    chat_region=[]
    skilling_region=[]
    bank_region=[]
    deposit_box_region=[]
    hp_region=[]
    prayer_region=[]
    stamina_region=[]
    attack_power_region=[]
    debug=False
    screenshot=None
    offset=None

    
    #TO DO: Minimap, health, prayer, stamina, special power
    

    def __init__(self, client_name, debug=True, state=None):
        ### properties ###
        #Haystacks
        self.client_haystack = Haystack(client_name)
        self.top_left       = [self.client_haystack.offset_x, self.client_haystack.offset_y]
        self.top_right      = [self.client_haystack.offset_x + self.client_haystack.w, self.client_haystack.offset_y]
        self.bottom_left    = [self.client_haystack.offset_x , self.client_haystack.offset_y + self.client_haystack.h]
        self.bottom_right   = [self.client_haystack.offset_x + self.client_haystack.w, self.client_haystack.offset_y + self.client_haystack.h]
        self.centre         = [self.client_haystack.offset_x+int(self.client_haystack.w/2) ,self.client_haystack.offset_y+int(self.client_haystack.h/2) ]
        self.inv_region      = append(add(self.bottom_right,self.INV_OFFSET_FROM_BR),self.INV_SIZE) #[x,y,w,h]
        self.chat_region     = append(add(self.bottom_left,self.CHAT_OFFSET_FROM_BL),self.CHAT_SIZE) #[x,y,w,h]
        self.skilling_region = append(add(self.top_left,self.SKILLING_OFFSET_FROM_TL),self.SKILLING_SIZE) #[x,y,w,h]
        # The bank offest is not linear, it is a hybrid function depending on whether the hight of the handle is <967 or >=967 
        # This is the point where the chat window and bank window seperate. 
        if self.client_haystack.h < 967:
            self.bank_region = append(add(self.top_left,
                                          add(self.BANK_OFFSET_INITIAL,[int((self.client_haystack.w-self.CLIENT_SIZE_INTIAL[0])/2),0])),
                                      add(self.BANK_SIZE_INITIAL, [0, int(self.client_haystack.h-self.CLIENT_SIZE_INTIAL[1])]))
        else: 
            extra_h = self.client_haystack.h-463
            BANK_OFFSET = add(self.BANK_OFFSET_INITIAL, [int((self.client_haystack.w-self.CLIENT_SIZE_INTIAL[0])/2), int(extra_h/2)]) 
            BANK_SIZE = add(self.BANK_SIZE_INITIAL, [0,int(463+(extra_h/2))])
            self.bank_region = append(add(self.top_left, BANK_OFFSET),BANK_SIZE)

        self.deposit_box_region = append(add(self.top_left,
                                            add([int((self.client_haystack.w-self.CLIENT_SIZE_INTIAL[0])/2),int((self.client_haystack.h-self.CLIENT_SIZE_INTIAL[1])/2)],self.DESPOSIT_BOX_OFFSET_INITIAL))
                                        , self.DESPOSIT_BOX_OFFSET_SIZE)
        self.health_region       = append(add(self.top_right,self.HEALTH_OFFSET_FROM_TR),self.HEALTH_SIZE) #[x,y,w,h]
        self.prayer_region       = append(add(self.top_right,self.PRAYER_OFFSET_FROM_TR),self.PRAYER_SIZE) #[x,y,w,h]
        self.stamina_region      = append(add(self.top_right,self.STAMINA_OFFSET_FROM_TR),self.STAMINA_SIZE) #[x,y,w,h]
        self.attack_power_region = append(add(self.top_right,self.ATTACK_POWER_OFFSET_FROM_TR),self.ATTACK_POWER_SIZE) #[x,y,w,h]

        self.inv_haystack      = Haystack(client_name, cropped_region=self.inv_region)
        self.chat_haystack     = Haystack(client_name, cropped_region=self.chat_region)
        self.skilling_haystack = Haystack(client_name, cropped_region=self.skilling_region)
        self.bank_haystack     = Haystack(client_name, cropped_region=self.bank_region)
        self.deposit_box_haystack  = Haystack(client_name, cropped_region=self.deposit_box_region)
        self.health_haystack       = Haystack(client_name, cropped_region=self.health_region)
        self.prayer_haystack       = Haystack(client_name, cropped_region=self.prayer_region)
        self.stamina_haystack      = Haystack(client_name, cropped_region=self.stamina_region)
        self.attack_power_haystack = Haystack(client_name, cropped_region=self.attack_power_region)

        self.debug=debug
        self.screenshot=None
        self.offset=None

        #if self.debug:
            #Client
            #client_screenshot, offset = self.client_haystack.get_screenshot()
            #cv.imshow('DEBUG MODE.jpeg', client_screenshot)
            #Inv
            #Skilling
            #Chat

    ### --------------- DEBUGGING Start --------------- ###

    """def show_windows(self, regions=['client']):
        haystacks=[]
        haystack_imgs=[]
        haystack_offsets=[]
        for region in regions:
            haystack=self.get_haystack(region)
            haystack_img, offset = haystack.get_screenshot()
            haystacks.append(haystack)
            haystack_imgs.append(haystack_img)
            haystack_offsets.append(haystack_offsets)
        for i in range(0,len(haystack_imgs)):
            cv.imshow('DEBUG - {region[i]}.jpeg', haystack_img[i])
    """

    ### --------------- DEBUGGING End --------------- ###

    ### --------------- HAND Start --------------- ###

    def click(self, coord, side='left', randomizeCoord=True, move=False, speed=2000):
        #coord = Coordinates
        #side = which mouse botton to click: left, riht, middle.
        #randomizeCoord adds a bit of randomization to the final coordinates
        #move determines if the mouse should move to its new location. move=False simply clicks the final coordinates
        #speed=2000 -> 2000px per 1sec if move=True
        if coord is None: return False
        x_coord=coord[0]
        y_coord=coord[1]

        if randomizeCoord:

            w=randint(7,15) #these w and h values are just guesses. Would be better if you were passed the img's actual w and h data.
            h=randint(7,15)
            x_sd=w/4
            y_sd=h/4

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

            dur=dis/speed + 0.01*uniform(-5,5)

        if self.debug: print(f"DEBUGGING: clicking at ({x_coord},{y_coord}).")
        pyautogui.click(x_coord, y_coord, button=side, duration=dur)

    @staticmethod
    def write(self, key, duration=normalvariate(0.06,0.011)):
        if self.debug: print(f"DEBUGGING: writing {key}")
        for char in key:
            pyautogui.write(key)
            sleep(normalvariate(0.085,0.011))
    
    @staticmethod #I have no idea what @staticmethod does...
    def key_press(key, duration=normalvariate(0.06,0.011), debug=False):
        if debug: print(f"DEBUGGING: pressing {key}")
        pyautogui.keyDown(key)
        sleep(duration)
        pyautogui.keyUp(key)

        
    ### --------------- HAND End --------------- ###
    ### --------------- Sleep Start --------------- ###

    def clickSleeper(self, task='inv_item'):
        if self.debug: print(f"DEBUGGING: clickSleeper for {task}")
        if   task=='inv_item':             sleep(uniform(0.11,0.51))
        elif task=='withdraw':             sleep(uniform(0.02, 0.2))
        elif task=='close_bank':           sleep(uniform(0.07,0.3))
        elif task=='spam':                 sleep(normalvariate(0.05,0.011)+uniform(0.01, 0.02))
        elif task=='dropping_item':        sleep(normalvariate(0.08,0.011)+uniform(0.05, 0.4))
        elif task=='make':                 sleep(uniform(16.7,17.3)+uniform(0.1,1.3))
        elif task=='open_bank_or_deposit': sleep(uniform(0.09,0.2))
        elif task=='inv_open_close':       sleep(uniform(0.07,0.31))
        elif task=='setting_view':         sleep(uniform(0.03,0.31))
        elif task=='closing_chat':         sleep(normalvariate(0.1,0.025))

    def shortSleep(self, short_sleep_weight=12, short_sleep_av=3.5, short_sleep_sd=uniform(0.8,1.2)):
        short_sleep_check = randint(1,short_sleep_weight) 
        if self.debug: print(f'DEBUGGING: shortSleep: check is {short_sleep_check} out of {short_sleep_weight}')   
        if short_sleep_check == 1:                             
            short_sleep_time=normalvariate(short_sleep_av,short_sleep_sd)
            print(f'    Sleeping for: {round(short_sleep_time,2)} sec')
            sleep(short_sleep_time)
            # Can remove sleep check variable if happy to lose for debugging purposes
            # if randint(0,long_sleep_weight) == 1: 
            #   short_sleep_time=normalvariate(short_sleep_av,short_sleep_sd)
            #   print(f'    Sleeping for: {round(short_sleep_time,2)} sec')
            #   sleep(short_sleep_time)

    def longSleep(self, long_sleep_weight=150, long_sleep_av=180, long_sleep_sd=uniform(40,50)):
        long_sleep_check = randint(1,long_sleep_weight)
        if self.debug: print(f'DEBUGGING: shortSleep: check is {long_sleep_check} out of {long_sleep_weight}') 
        if long_sleep_check == 1:                       
            long_sleep_time=normalvariate(long_sleep_av,long_sleep_sd)
            print(f'    Sleeping for: {round(long_sleep_time,2)} sec')
            sleep(long_sleep_time)

    ### --------------- SLEEP End --------------- ###

    ### --------------- BOT FUNCTIONS Start --------------- ###

    ### 1. REMOVE????
    ### 2. Why would a script need to call bot.get_screenshot(region="")?? Remove this at some point
    ### 3. Replaced with get_haystack below
    #def get_screenshot(self, region='client'):
    #    if   region == 'client':     return self.client_haystack.get_screenshot()
    #   #elif region == 'bank':       return self.bank_haystack.get_screenshot()
    #    elif region == 'inv':        return self.inv_haystack.get_screenshot()
    #    elif region == 'skilling':   return self.skilling_haystack.get_screenshot() 
    #    elif region == 'chat':       return self.chat_haystack.get_screenshot()
    
    def get_haystack(self, region='client'):
        #if self.debug: print(f"DEBUGGING: getting haystack for {region}")
        if   region == 'client':       return self.client_haystack
        elif region == 'bank':         return self.bank_haystack
        elif region == 'inv':          return self.inv_haystack
        elif region == 'skilling':     return self.skilling_haystack
        elif region == 'chat':         return self.chat_haystack
        elif region == 'deposit_box':  return self.deposit_box_haystack
        elif region == 'health':       return self.health_haystack
        elif region == 'prayer':       return self.prayer_haystack
        elif region == 'stamina':      return self.stamina_haystack
        elif region == 'attack_power': return self.attack_power_haystack


    # Change on_screen to in_haystack or in_region??
    def on_screen(self, item, region='client', threshold=THRESHOLD, debug_mode=DEBUG_MODE):
        if self.debug: print(f"DEBUGGING: on screen check for {item.path} in {region}")
        haystack = self.get_haystack(region)
        coords = self.find_img(item, haystack, threshold=threshold) #TO DO: Update to return True once the first item has been found, takes too long to find all using find_img()
        return bool(coords)

    def find_contours(self, colour, region="client", key='dist', ignore_region=[0,0,0,0], debug=False, debug_img=None):
        if self.debug: print(f"DEBUGGING: find contours for {colour}")
        # lower and upper BGR values (NOT RGB!!)
        if   colour == 'blue':  colour_limits = [[150, 67,  0], [215, 215,  47]]
        elif colour == 'green': colour_limits = [[0, 190,  0], [20, 255, 20]]
        elif colour == 'yellow':colour_limits = [[0, 150,150], [50, 255, 255]] 
        elif colour == 'red':   colour_limits = [[0, 0,  28], [28, 28, 255]] # RED is bugging when used on 'client' since lots of red icons
        elif False: pass #TO DO: ADD OTHER COLOURS, RED AND BLUE
        else: print('No colour has been specified')

        screenshot, offset = self.get_haystack(region).get_screenshot()
        lower = array(colour_limits[0], dtype="uint8") #numpy.array() objects
        upper = array(colour_limits[1], dtype="uint8")
        mask = cv.inRange(screenshot, lower, upper)
        #if self.debug: print(f"DEBUGGING:       contour mask {mask}")
        output = cv.bitwise_and(screenshot, screenshot, mask=mask)
        ret, thresh = cv.threshold(mask, 40, 255, 0)    #WHAT DO THESE NUMBERS MEAN?
        contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        rectangles=[]

        if ignore_region!=[0,0,0,0]: ignore_region=self.get_haystack(ignore_region).cropped_region

        left_ignore, top_ignore, w_ignore, h_ignore = ignore_region
        right_ignore, bottom_ignore = (left_ignore+w_ignore,top_ignore+h_ignore)
        
        if len(contours) != 0:

            for contour in contours:
                rectangles.append(cv.boundingRect(contour))
                
            # Algorthim for removing contours that are *too large*, *too small*, or TOP_LEFT is in ignore_region 
            a=rectangles    # All intial contours
            b=[]            # Temp array to be sorted and filterd
            c=[]            # Final contours
            for rect in a:
                #    w > 6   and   h > 6        # TOP_LEFT is not in ignore_region
                if rect[2]>6 and rect[3]>6 and not ( left_ignore < rect[0] < right_ignore and top_ignore < rect[1] < bottom_ignore ): # Remove clear contours have have a dimension less than 10 (these are always errors)
                    b.append(rect)
            if len(b)==0: return  #If all contours found were errors then shortcut to returning false
            b=sorted(b, key=lambda rect: rect[2]*rect[3])   # Sort from smallest area to largest
            middleIndex=int((len(b))/2)
            median_rect = b[middleIndex]             
            median_area = median_rect[2]*median_rect[3]                 # Pick middle area
            for rect in b:
                if median_area*0.2 < rect[2]*rect[3] < median_area*6:
                    c.append(rect)
            rectangles=c

            if key == 'dist':
                closest_dist_to_centre=10000
                closest_to_centre=None
                for i in range(len(rectangles)):
                    x, y, w, h = rectangles[i]
                    dist_to_centre=sqrt((x+(w/2)-self.centre[0])**2+(y+(h/2)-self.centre[1])**2)
                    if dist_to_centre < closest_dist_to_centre:
                            closest_dist_to_centre=dist_to_centre
                            closest_to_centre=[x,y,w,h]
                x, y, w, h = closest_to_centre 

            elif key == 'max_area':
                x, y, w, h = rectangles[-1]
                # find the biggest countour (c) by the area
                #contour = max(contours, key=cv.contourArea)
                #x, y, w, h = cv.boundingRect(contour)

            elif key == 'min_area':
                x, y, w, h = rectangles[0]

            center_x = x + int(w/2)
            center_y = y + int(h/2)

            center_point_with_offset=tuple(add((center_x, center_y),offset)) 
        
            if self.debug:
                print(f"number of contours found: {len(rectangles)}")
                for (x ,y, w, h) in rectangles:
                    #print(f"x, y, w, h values of contours: {x, y, w, h}")
                    print(f"{x, y, w, h},")
                # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                # Draw rectangles
                    cv.rectangle(debug_img, top_left, bottom_right, color=(0, 0, 255), thickness=2)
                        # Draw point at centre of rectangles
                    if key=='dist': 
                        centre = (int(x+w/2),int(y+h/2))
                        cv.drawMarker(debug_img, centre, 
                                color=(0, 255, 255), markerType=cv.MARKER_CROSS, 
                                markerSize=5, thickness=2)


                # Draw contours
                # cv.drawContours(debug_img, contours, -1, (0, 255, 0), 3)
                
                # Draw centre of img
                if key == 'dist':
                    cv.drawMarker(debug_img, self.centre, 
                                color=(255, 0, 255), markerType=cv.MARKER_CROSS, 
                                markerSize=20, thickness=2)
                
            return center_point_with_offset
        else:
            return 

    def find_img(self, needle, haystack, threshold=0.7, greyscale=False, debug_mode=None, debug_img=None):
        if self.debug: print(f"DEBUGGING:       finding {needle.path} ")
        haystack_img, offset = haystack.get_screenshot()
        result = cv.matchTemplate(haystack_img, needle.needle_img, needle.method)

        locations = where(result >= threshold) # Need to add option for inverted comparison methods
        locations = list(zip(*locations[::-1]))
        
        rectangles = []

        for loc in locations:

            rect = [int(loc[0]), int(loc[1]), needle.needle_w, needle.needle_h]

            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        
        ### Below is for Debugging ### 
        if self.debug:
            #print(f'   Locations found: {len(locations)}')
            print(f'    Grouped locations found: {len(rectangles)}')
            #print(f"   Rectangles (x,y,w,h): {rectangles}")

        center_points = []

        if len(rectangles):

            line_colour = (0,255,0)
            line_type = cv.LINE_4
            marker_colour = (255, 0, 255)
            marker_type=cv.MARKER_CROSS

            for (x ,y, w, h) in rectangles:

                center_x = x + int(w/2)
                center_y = y + int(h/2)

                center_points_with_offset=tuple(add((center_x, center_y),offset))

                center_points.append(center_points_with_offset)

                if self.debug and debug_mode == 'rectangles':
                    # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the box
                    cv.rectangle(debug_img, top_left, bottom_right, color=line_colour, 
                                lineType=line_type, thickness=2)
                elif self.debug and debug_mode == 'points':
                    # Draw the center point
                    cv.drawMarker(debug_img, (center_x, center_y), 
                                color=marker_colour, markerType=marker_type, 
                                markerSize=40, thickness=2)

        #if debug:
        #    cv.imwrite('vision.py - DEBUG MODE.jpeg', haystack_img)
        
        if self.debug: print(f'    Center Points: {center_points}')

        return center_points

    def extract_text(self, image, scale=1, config='--psm 1', lang='eng'):
        image=cv.resize(image,None, fx=scale, fy=scale)
        extracted_text = pytesseract.image_to_string(image, lang=lang, config=config) # --psm 6 -> Assume a single uniform block of text.
        processed_text = ' '.join(extracted_text.split())
        return processed_text
        
    def open_bank(self):
        for i in range(randint(2,4)+randint(0,3)+randint(0,1)):
            #haystack = self.get_haystack('client')
            #coords = self.find_img(open_bank_icon, haystack, threshold=0.5)
            #hand.click(coords) # Red square was too buggy, need alternate solution
            self.click([466,335])
            self.clickSleeper('spam')
        self.clickSleeper('close_bank')

    def withdraw(self, items, threshold=THRESHOLD, debug_mode=DEBUG_MODE, randomizeCoord=RANDOMIZE_COORDS):
        for needle in items:
            haystack = self.get_haystack('bank')
            coords = self.find_img(needle, haystack)
            self.click(coords[0]) #0 index used in debugging
            self.clickSleeper('withdraw')

    def close_bank(self):
        self.key_press('esc')
        self.clickSleeper('close_bank')

    def make(self, items, threshold=THRESHOLD, debug_mode=DEBUG_MODE, randomizeCoord=RANDOMIZE_COORDS):
        for needle in items:
            haystack = self.get_haystack('inv')
            coords = self.find_img(needle, haystack)
            self.click(coords[0])
            self.clickSleeper('inv_item')
        if self.on_screen(all_icon_unselected, threshold=0.90):
            haystack = self.get_haystack('client')
            coords = self.find_img(all_icon_unselected,haystack)
            self.click(coords[0])
            self.clickSleeper('inv_item')
        self.key_press('space')
        self.clickSleeper('spam')
        if randint(0,1)== 0:  self.key_press('space')
        self.clickSleeper('make')

    def deposit(self):
        coord = self.find_img(deposit, self.client_haystack)
        for i in range(randint(2,4)+randint(0,3)+randint(0,1)):
            self.click(coord[0])
            self.clickSleeper('spam')

    def read_stat(self, stat, scale=7):
        colour_limits = [[0, 0,  0], [0, 255, 0]] #Limits for GREEN

        lower = array(colour_limits[0], dtype="uint8") #numpy.array() objects
        upper = array(colour_limits[1], dtype="uint8")

        haystack_img, offset = self.get_haystack(stat).get_screenshot()
        haystack_mask = cv.inRange(haystack_img, lower, upper)
        haystack_masked_img = cv.bitwise_and(haystack_img, haystack_img, mask=haystack_mask) 
        #grayscale_img = cv.cvtColor(haystack_masked_img, cv.COLOR_BGR2GRAY)      
        _, threshold_img = cv.threshold(haystack_masked_img, 40, 255, 0)

        return self.extract_text(threshold_img, scale=scale, config='--psm 6').lower()
    
    def click_attack_power(self, thres):
        value=self.read_stat('attack_power')
        try: value=int(value)
        except: return 
        if value>=thres: 
            x,y,w,h = self.attack_power_region
            coord=(uniform(x,x+w),uniform(y,y+h))
            self.click(coord, randomizeCoord=False)
            self.clickSleeper('inv_item')

    def skilling_check(self, skill, config='--psm 1'):
        colour_limits = [[0, 0,  0], [0, 255, 255]] #Limits for RED and GREEN

        lower = array(colour_limits[0], dtype="uint8") #numpy.array() objects
        upper = array(colour_limits[1], dtype="uint8")

        haystack_img, offset = self.get_haystack('skilling').get_screenshot()
        haystack_mask = cv.inRange(haystack_img, lower, upper)
        haystack_masked_img = cv.bitwise_and(haystack_img, haystack_img, mask=haystack_mask)      
        _, haystack_masked_img = cv.threshold(haystack_masked_img, 40, 255, 0)
        haystack_masked_img = cv.cvtColor(haystack_masked_img, cv.COLOR_BGR2GRAY) 

        extracted_text=self.extract_text(haystack_masked_img, config=config).lower()
        
        #FOR DEBUGGING
        if self.debug:
            print(f'Skilling text: {self.extract_text(haystack_masked_img)}')
            cv.imshow('haystack_masked_img.jpeg', haystack_masked_img)
        #cv.imshow('needle_masked_img.jpeg', text_needle.needle_img)
        
                #Need to upgrade this if, elif, else statement to handle cooking AND fishing (or any other scripts which require 2 skills at once)
        #print("                " + extracted_text)
        if "not" in extracted_text:
        #    print("NOT")
            return False
        elif skill in extracted_text:
        #    print("skill")
            return True
        else:
        #    print("None")
            return False

        # PREVIOUS VERSION where needle was attempted to be found in haystack
        #if   "not" in skill: NOT=True
        #else:                NOT=False
        #
        #if NOT: # "not" is in skilling text, look for red text
        #    text_needle = Needle("Images\\skilling_" + skill +  ".jpg")
        #    colour_limits = [[, ,  ], [, , ]] #Limits for RED
        #else: #  "not" is not in skilling text, look for green text
        #    text_needle = Needle("Images\\skilling_" + skill +  ".jpg")
        #    colour_limits = [[0, 28,  0], [20, 255, 80]] #Limits for GREEN
        #text_img = text_needle.needle_img        
        #needle_mask =  cv.inRange(text_img, lower, upper)
        #needle_masked_img = cv.bitwise_and(text_img, text_img, mask=needle_mask)
        #result = cv.matchTemplate(haystack_masked_img, text_needle.needle_img, text_needle.method)
        #locations = where(result >= 0.6)
        #locations = list(zip(*locations[::-1]))
        #if len(locations):
        #    if self.debug: print("Images\\skilling_" + skill +  ".jpg has been FOUND")
        #    return True
        #else:
        #    print("No skilling text has been identified")
        #    return False
        #else:
        #    print("Can't tell if " + skill + " or not.... Setting check as False. :(")
        #    return False
    


    def open_inv(self):
        if self.debug: print(f"DEBUGGING:       opening inv ")
        if self.on_screen(inv_open_needle, region='inv', threshold=.8):
            print("Inventory is already open.")
        elif self.on_screen(inv_closed_needle, region='inv', threshold=.8):
            self.key_press('esc', debug=self.debug)
            self.clickSleeper('inv_item')
            print("Inventory was closed, now open.")
        else:
            print('No inventory icon detected.')

    def set_view(self, scroll_out=False):
        if self.debug: print(f"DEBUGGING:       setting view")
        #click compass to set North view
        compass_coords = add(self.top_right,self.COMPASS_OFFSET_FROM_TR)
        self.click(compass_coords)
        self.clickSleeper('inv_item')
        #click "up" to raise camera view
        self.key_press("up", uniform(1.91,2.82))
        self.clickSleeper('closing_chat')
        #TO DO scroll out
        if scroll_out:
            pass

    def close_chat(self):
        if self.debug: print(f"DEBUGGING:       closing chat")
        if self.on_screen(Needle('Images\\press_enter_to_chat.jpg'),region='chat'):
            print('Chat is open.')
            all_coord=add(self.bottom_left, self.CHAT_ALL_OFFSET_FROM_BL) 
            all_coord=add(all_coord,[randint(-15,15),randint(-8,8)])
            self.click(all_coord, randomizeCoord=False)
            self.clickSleeper('closing_chat')
            self.close_chat() #Should trigger maximum of two times. Once to open/close the "All" chat, another to guraentee the close.
        print('Chat open needle was not detected.')    

    def count_fish(self, fish_needles):
        if self.debug: print(f"DEBUGGING:       counting fish")
        count=0
        for fish_needle in fish_needles:
            count += len(self.find_img(fish_needle,self.inv_haystack, threshold=0.975))
        print(f"{count} fish in inventory")
        return count
    
    def count_gems(self, gem_needles):
        if self.debug: print(f"DEBUGGING:       counting gems")
        count=0
        for gem_needle in gem_needles:
            count += len(self.find_img(gem_needle, self.inv_haystack, threshold=0.8))
        print(f"{count} gems in inventory")
        return count
    
    def check_all_is_selected(self, big=False):
        if self.debug: print(f"DEBUGGING:       checking if all is selected")
        
        if big: needle=all_icon_unselected_BIG
        else:   needle=all_icon_unselected
        
        if self.on_screen(needle,region='deposit_box'): #region='client' is to be changed to 'deposit box'
            print('all is unselected.')
            self.click(self.find_img(needle,self.get_haystack('deposit_box')))
            self.clickSleeper('all has been selected')

        #^^^    check_all_is_selected was very shotily put together, need to revise.


    def count_clues(self, skill=None):
        #if self.debug: print(f"DEBUGGING:       counting clues")
        return 0 #TO DO
    
    def count_bird_nests(self, skill=None):
        #if self.debug: print(f"DEBUGGING:       counting clues")
        return 0 #TO DO
    
    def drop_fish(self, fish_needles): #ASSUMPTIONS: Left-click has been swapped with 'drop'. TO DO: Cooked fish
        if self.debug: print(f"DEBUGGING:       dropping fish")
        for fish_needle in fish_needles:
            coords = self.find_img(fish_needle,self.inv_haystack)
            sorted(coords)
            for coord in coords:
                self.click(coord)
                self.clickSleeper('dropping_item')
                self.shortSleep(40)
                self.longSleep()

    def bank_is_open(self):
        haystack_img, offset=self.get_haystack('bank').get_screenshot()
        w,h,c = haystack_img.shape
        left=60
        right=w-375
        top=5
        bottom=30
        haystack_img = haystack_img[top:bottom, left:right]
        colour_limits = [[20, 100,  200], [40, 200, 255]] #Limits for RED and GREEN
        lower = array(colour_limits[0], dtype="uint8") #numpy.array() objects
        upper = array(colour_limits[1], dtype="uint8")
        haystack_mask = cv.inRange(haystack_img, lower, upper)
        haystack_masked_img = cv.bitwise_and(haystack_img, haystack_img, mask=haystack_mask) 
        #grayscale_img = cv.cvtColor(haystack_masked_img, cv.COLOR_BGR2GRAY)      
        _, haystack_img = cv.threshold(haystack_masked_img, 40, 255, 0)

        extracted_text=self.extract_text(haystack_img).lower()
        
        #FOR DEBUGGING
        #print(self.extract_text(haystack_img))
        #cv.imshow('haystack_masked_img.jpeg', haystack_img)
        #cv.imshow('needle_masked_img.jpeg', text_needle.needle_img)
        
                #Need to upgrade this if, elif, else statement to handle cooking AND fishing (or any other scripts which require 2 skills at once)
        #print("                " + extracted_text)
        if ("the" in extracted_text) or ("bank" in extracted_text) or ("of" in extracted_text):
            print("Yes")
            return True
        else:
            print("No")
            return False
        # Previous version, good not great, could be buggy
        #return self.on_screen(deposit_box__title, 'deposit_box') #region='client' is to be changed to 'deposit box'
        
        
        #return self.on_screen(bank_title, region='bank')
    
    def despoit_box_is_open(self):
        haystack_img, offset=self.get_haystack('deposit_box').get_screenshot()
        w,h,c = haystack_img.shape
        left=60
        right=w-375
        top=5
        bottom=30
        haystack_img = haystack_img[top:bottom, left:right]
        colour_limits = [[20, 100,  200], [40, 200, 255]] #Limits for RED and GREEN
        lower = array(colour_limits[0], dtype="uint8") #numpy.array() objects
        upper = array(colour_limits[1], dtype="uint8")
        haystack_mask = cv.inRange(haystack_img, lower, upper)
        haystack_masked_img = cv.bitwise_and(haystack_img, haystack_img, mask=haystack_mask) 
        #grayscale_img = cv.cvtColor(haystack_masked_img, cv.COLOR_BGR2GRAY)      
        _, threshold_img = cv.threshold(haystack_masked_img, 40, 255, 0)

        extracted_text=self.extract_text(threshold_img).lower()
        
        #FOR DEBUGGING
        print(self.extract_text(haystack_img))
        cv.imshow('haystack_masked_img.jpeg', haystack_img)
        #cv.imshow('needle_masked_img.jpeg', text_needle.needle_img)
        
                #Need to upgrade this if, elif, else statement to handle cooking AND fishing (or any other scripts which require 2 skills at once)
        #print("                " + extracted_text)
        if ("the" in extracted_text) or ("bank" in extracted_text) or ("of" in extracted_text):
        #    print("NOT")
            return True
        else:
        #    print("None")
            return False
        # Previous version, good not great, could be buggy
        #return self.on_screen(deposit_box__title, 'deposit_box') #region='client' is to be changed to 'deposit box'

    def count_logs(self, log_needle):
        if self.debug: print(f"DEBUGGING:       counting logs")
        count=0
        count += len(self.find_img(log_needle,self.inv_haystack, threshold=0.9))
        print(f"{count} logs in inventory")
        return count

    def drop_logs(self, log_needle): #ASSUMPTIONS: Left-click has been swapped with 'drop'. TO DO: Cooked fish
        if self.debug: print(f"DEBUGGING:       dropping logs")
        coords = self.find_img(log_needle,self.inv_haystack)
        sorted(coords)
        for coord in coords:
            self.click(coord)
            self.clickSleeper('dropping_item')
            self.shortSleep()
            self.longSleep()

    def click_item_in_inv(self, needle):
        coords = self.find_img(needle, self.get_haystack('inv'))
        self.click(coords[randint(0,len(coords)-1)])
        self.clickSleeper('inv')
    ### --------------- BOT FUNCTIONS End --------------- ###




# initalizing Needles, Haystack, and Hand
# NEED TO MOVE THESE TO INDIVIDUAL SCRIPTS
ready_to_make =         Needle('Images\\ready_to_make_confirmation.jpg')
all_icon_unselected =   Needle('Images\\all_icon_unselected.jpg')
all_icon_selected =     Needle('Images\\all_icon_selected.jpg')
open_bank =             Needle('Images\\open_bank.jpg')
bank_title=             Needle('Images\\bank_title.jpg')
deposit =               Needle('Images\\deposit.jpg')
open_bank_icon =        Needle('Images\\red_square.jpg')
inv_open_needle =       Needle('Images\\inv_open.jpg')
inv_closed_needle =     Needle('Images\\inv_closed.jpg')
chat_open_needle =      Needle('Images\\press_enter_to_chat.jpg')
all_icon_unselected_BIG =   Needle('Images\\all_icon_unselected_BIG.jpg')
all_icon_selected_BIG =     Needle('Images\\all_icon_selected_BIG.jpg')
deposit_box__title=     Needle('Images\\deposit_box_title.jpg')