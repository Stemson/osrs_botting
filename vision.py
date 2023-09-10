import cv2 as cv
import numpy as np
import win32gui
import win32ui
import win32con

class Needle:

    # class properties

    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    # constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):

        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        self.method=method
        pass

    def find(self, haystack_img, offset=[0,0], threshold=0.7, debug_mode=None):

        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        locations = np.where(result >= threshold) # Need to add option for inverted comparison methods
        locations = list(zip(*locations[::-1]))
        
        rectangles = []

        for loc in locations:

            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]

            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        
        ### Below is for Debugging ### 
        print(f'# Locations found: {len(locations)}')
        print(f'# Grouped locations found: {len(rectangles)}')
        print(f"Rectangles (x,y,w,h): {rectangles}")

        center_points = []

        if len(rectangles):

            line_colour = (0,255,0)
            line_type = cv.LINE_4
            marker_colour = (255, 0, 255)
            marker_type=cv.MARKER_CROSS

            for (x ,y, w, h) in rectangles:

                center_x = x + int(w/2)
                center_y = y + int(h/2)

                center_points_with_offset=tuple(np.add((center_x, center_y),offset))

                center_points.append(center_points_with_offset)

                if debug_mode == 'rectangles':
                    # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the box
                    cv.rectangle(haystack_img, top_left, bottom_right, color=line_colour, 
                                lineType=line_type, thickness=2)
                elif debug_mode == 'points':
                    # Draw the center point
                    cv.drawMarker(haystack_img, (center_x, center_y), 
                                color=marker_colour, markerType=marker_type, 
                                markerSize=40, thickness=2)

        #if debug_mode:
        #    cv.imshow('vision.py - DEBUG MODE', haystack_img)
            #cv.imwrite('vision.py - DEBUG MODE', haystack_img)
        
        print(f'Center Points: {center_points}')

        return center_points


class Haystack:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name=None,cropped_region=None):
        # find the handle for the window we want to capture   ### DEBUG CHECK: GOOD
        if window_name==None: self.hand = win32gui.GetDesktopWindow()
        else:                 self.hwnd = win32gui.FindWindow(None, window_name)
        
        #Leftover code - Delete?
        #if not self.hwnd:
        #    raise Exception(f'Window not found: {window_name}')

        # get the window size
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        self.w = right - left
        self.h = bottom - top           

        # account for the window border and titlebar and cut them off

        if cropped_region==None:  
            border_pixels = 4
            titlebar_pixels = 27
            self.w = self.w - (border_pixels * 2)
            self.h = self.h - titlebar_pixels - border_pixels
            self.cropped_x = border_pixels
            self.cropped_y = titlebar_pixels
        else: #cropped_region = [x,y,w, h]
            self.cropped_x, self.cropped_y, self.w, self.h = cropped_region

        # set the cropped coordinates offset so we can translate screenshot
        # coordinates into actual screen coordinates
        self.offset_x = left + self.cropped_x
        self.offset_y = top + self.cropped_y

    def get_screenshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
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
        img = np.ascontiguousarray(img)

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


'''
    def findMax(haystack_img, needle_img, threshold=0.7, method=cv.TM_CCOEFF_NORMED, debug_mode=None):

        result = cv.matchTemplate(haystack_img, needle_img, method)

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        print('Best match top left position: %s' % str(max_loc))
        print('Best match confidence: %s' % max_val)

        if max_val >= threshold:

            top_left = max_loc
            bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)

            h = needle_img.shape[0]
            w = needle_img.shape[1]

            center_x = top_left[0] + int(w/2)
            center_y = top_left[0] + int(h/2)
                
        else:   
            print('Needle not found.')

        if debug_mode == 'rectangles':
            # Determine the box position
            # Draw the box
            cv.rectangle(haystack_img, top_left, bottom_right, color=(0,255,0), 
                            lineType=cv.LINE_4, thickness=2)
        elif debug_mode == 'points':
            # Draw the center point
            cv.drawMarker(haystack_img, (center_x, center_y), 
                            color=(255, 0, 255), markerType=cv.MARKER_CROSS, 
                            markerSize=40, thickness=2)

        if debug_mode:
            cv.imshow('Needle Found', haystack_img)
            cv.waitKey()
            #cv.imwrite('result_click_point.jpg', haystack_img)

        return ((center_x,center_y))
'''
