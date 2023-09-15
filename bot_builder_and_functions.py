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


class Bot(Haystack,Needle):
    # constants
    OFFSET=[0,0]                   # This surely isnt right, OFFSET will need to updated to be 
    THRESHOLD = 0.9                # Consider making individual thresholds for needles
    DEBUG_MODE = 'rectangles'
    RANDOMIZE_COORDS=True
    BANK_REGION = [36,27, 484, 335] # [x,y,w,h] #TO DO: Update abnk region to be dynamic (similar to inv, chat, and skilling)
    GE_REGION = []
    INV_REGION = [580, 194, 172, 250] #Change to dimensions and offset_from_BR
    INV_SIZE = [250,370]
    INV_OFFSET_FROM_BR = [-1*x for x in INV_SIZE] #[-200,-344]  #ASSUMPTION: Both menu bars are stacked. i.e. game window wisth is less than 990 pixels. 
    CHAT_SIZE = [520,170]
    CHAT_OFFSET_FROM_BL = [0,-CHAT_SIZE[1]] #[0,-166]
    CHAT_ALL_OFFSET_FROM_BL = [32,-15]
    SKILLING_SIZE = [175,200]
    SKILLING_OFFSET_FROM_TL = [0,0] #[0,0]
    COMPASS_OFFSET_FROM_TR = [-158, 21]

    # properties
    client_haystack=None
    inv_haystack=None
    chat_haystack=None
    skilling_haystack=None
    top_left=[]
    top_right=[]
    bottom_left=[]
    bottom_right=[]
    centre=[]
    inv_region=[]
    chat_region=[]
    skilling_region=[]
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
        self.centre         = [self.left+(self.w/2)    ,self.top+(self.h/2) ]
        
        # bank_region = 
        # self.bank_haystack   = Haystack(client_name, cropped_region=bank_region)
        self.inv_region      = append(add(self.bottom_right,self.INV_OFFSET_FROM_BR),self.INV_SIZE) #[x,y,w,h]
        self.chat_region     = append(add(self.bottom_left,self.CHAT_OFFSET_FROM_BL),self.CHAT_SIZE) #[x,y,w,h]
        self.skilling_region = append(add(self.top_left,self.SKILLING_OFFSET_FROM_TL),self.SKILLING_SIZE) #[x,y,w,h]

        self.inv_haystack      = Haystack(client_name, cropped_region=self.inv_region)
        self.chat_haystack     = Haystack(client_name, cropped_region=self.chat_region)
        self.skilling_haystack = Haystack(client_name, cropped_region=self.skilling_region)

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
        if self.debug: print(f"DEBUGGING: getting haystack for {region}")
        if   region == 'client':     return self.client_haystack
       #elif region == 'bank':       return self.bank_haystack
        elif region == 'inv':        return self.inv_haystack
        elif region == 'skilling':   return self.skilling_haystack
        elif region == 'chat':       return self.chat_haystack
    
    # Change on_screen to in_haystack or in_region??
    def on_screen(self, item, region='client', threshold=THRESHOLD, debug_mode=DEBUG_MODE):
        if self.debug: print(f"DEBUGGING: on screen check for {item.path} in {region}")
        haystack = self.get_haystack(region)
        coords = self.find_img(item, haystack, threshold=threshold)
        return bool(coords)

    def find_contours(self, colour, region="client", key='dist', debug=False, debug_img=None):
        if self.debug: print(f"DEBUGGING: find contours for {colour}")
        # lower and upper BGR values (NOT RGB!!)
        if   colour == 'blue':  colour_limits = [[67, 67,  0], [225, 215,  47]]
        elif colour == 'green': colour_limits = [[0, 76,  20], [46, 255, 54]]
        elif colour == 'yellow':colour_limits = [[0, 120,120], [50, 255, 255]] 
        elif colour == 'red':   colour_limits = [[8, 8,  80], [28, 28, 255]] #RED is bugging when used on 'client' since lots of red icons
        elif True: pass #TO DO: ADD OTHER COLOURS, RED AND BLUE

        screenshot, offset = self.get_haystack(region).get_screenshot()
        lower = array(colour_limits[0], dtype="uint8") #numpy.array() objects
        upper = array(colour_limits[1], dtype="uint8")
        mask = cv.inRange(screenshot, lower, upper)
        #if self.debug: print(f"DEBUGGING:       contour mask {mask}")
        output = cv.bitwise_and(screenshot, screenshot, mask=mask)
        ret, thresh = cv.threshold(mask, 40, 255, 0)    #WHAT DO THESE NUMBERS MEAN?
        contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        if len(contours) != 0:
            if key== 'dist':
                closest_dist_to_centre=1000
                closest_to_centre=None
                for contour in contours:
                    x, y, w, h = cv.boundingRect(contour)
                    dist_to_centre=sqrt(((x+w/2)-self.centre[0])**2+((y+h/2)-self.centre[1])**2)
                    if dist_to_centre < closest_dist_to_centre:
                            closest_dist_to_centre=dist_to_centre
                            closest_to_centre=[x,y,w,h]
                #print(len(contours))
                
                #contour = min(contours, key=self.dist_from_centre)            
                # find contour which is closet to the centre of the haystack
                # contour_closest_to_centre = max(contours, key=dist_from()) 
                # contour_closest_to_centre = max(contours, key=lambda k: ) 
                #print(contours)

                x, y, w, h = closest_to_centre
            elif key == 'area':
                # find the biggest countour (c) by the area
                contour = max(contours, key=cv.contourArea)
                x, y, w, h = cv.boundingRect(contour)
            
            if self.debug: image = cv.rectangle(screenshot, pt1=(x, y), pt2=(x+w, y+h), color=(0, 0, 255), thickness=2)
            
            center_x = x + int(w/2)
            center_y = y + int(h/2)

            center_point_with_offset=tuple(add((center_x, center_y),offset)) 
        
            if self.debug:
                print("x, y, w, h values of contours")
                print(x, y, w, h)
                # Determine the box position
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                # Draw contours
                cv.drawContours(debug_img, contours, -1, (0, 255, 0), 3)
                
            return center_point_with_offset
        else:
            return False

    def find_img(self, needle, haystack, threshold=0.7, debug_mode=None, debug_img=None):
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
        
        print(f'    Center Points: {center_points}')

        return center_points

    def bank_is_open(self):
        return self.on_screen(bank_title, region='bank')
        
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

    def skilling_check(self, skill):
        if   "not" in skill: NOT=True
        else:                NOT=False
        
        if NOT: # "not" is in skilling text, look for red text
            text_img = Needle("Images\\skilling_" + skill +  "_not.jpg")
            colour_limits = [[8, 8,  100], [28, 28, 205]] #Limits for RED
        else: #  "not" is not in skilling text, look for green text
            text_img = Needle("Images\\skilling_" + skill +  ".jpg")
            colour_limits = [[0, 76,  20], [46, 255, 54]] #Limits for GREEN
        
        lower = array(colour_limits[0], dtype="uint8") #numpy.array() objects
        upper = array(colour_limits[1], dtype="uint8")

        haystack_img, offset = self.get_haystack('skilling').get_screenshot()
        
        mask = cv.inRange(haystack_img, lower, upper)
        #if self.debug: print(f"DEBUGGING:       contour mask {mask}")
        masked_img = cv.bitwise_and(haystack_img, haystack_img, mask=mask)
        
        result = cv.matchTemplate(masked_img, text_img.needle_img, text_img.method)

        locations = where(result >= 0.9)
        locations = list(zip(*locations[::-1]))
        
        if len(locations)>0:
            return True
        else:
            return False
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
            count += len(self.find_img(gem_needle, self.inv_haystack, threshold=0.975))
        print(f"{count} gems in inventory")
        return count
    
    def check_all_is_selected(self, big=False):
        if self.debug: print(f"DEBUGGING:       checking if all is selected")
        
        if big: needle=all_icon_unselected_BIG
        else:   needle=all_icon_unselected
        
        if self.on_screen(needle,region='client'): #region='client' is to be changed to 'deposit box'
            print('all is unselected.')
            self.click(self.find_img(needle,self.get_haystack('client')))
            self.clickSleeper('all has been selected')

        #^^^    check_all_is_selected was very shotily put together, need to revise.


    def count_clues(self, skill=None):
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

    def despoit_box_is_open(self):
        return self.on_screen(deposit_box__title, 'client')

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