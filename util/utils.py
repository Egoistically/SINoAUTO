import cv2, numpy, time, pyautogui
from random import randint, uniform
from util.adb import Adb
from datetime import datetime

class Region(object):
    x, y, w, h = 0, 0, 0, 0

    def __init__(self, x, y, w, h):
        """Initializes a region.
        Args:
            x (int): Initial x coordinate of the region (top-left).
            y (int): Initial y coordinate of the region (top-left).
            w (int): Width of the region.
            h (int): Height of the region.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

screen = None

class Utils(object):
    screen = None
    DEFAULT_SIMILARITY = 0.95
    swipe = []

    @staticmethod
    def script_sleep(base=None, flex=None):
        """Put script to sleep.
        Args:
            base (int, optional): Minimum amount of time to go to sleep for.
            flex (int, optional): The delta for the max amount of time to go
                to sleep for.
        """
        if base is None:
            time.sleep(uniform(0.4, 0.7))
        else:
            flex = base / 2 if flex is None else flex
            time.sleep(uniform(base, base + flex))

    @staticmethod
    def multithreader(threads):
        """Method for starting and threading multithreadable Threads in
        threads.
        Args:
            threads (list): List of Threads to multithread.
        """
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    @classmethod
    def update_screen(cls):
        """Uses ADB to pull a screenshot of the device and then read it via CV2
        and then stores the images in grayscale and color to screen and color_screen, respectively.
        Returns:
            image: A CV2 image object containing the current device screen.
        """
        global screen
        screen = None

        while screen is None:
            screen = cv2.imdecode(numpy.frombuffer(Adb.exec_out('screencap -p'), dtype=numpy.uint8), cv2.IMREAD_COLOR)

        cls.screen = screen

    @classmethod
    def wait_update_screen(cls, time=None):
        """Delayed update screen.
        Args:
            time (int, optional): seconds of delay.
        """
        if time is None:
            cls.script_sleep()
        else:
            cls.script_sleep(time)
        cls.update_screen()

    @classmethod
    def find(cls, image, similarity=DEFAULT_SIMILARITY):
        """Finds the specified image on the screen
        Args:
            image (string): [description]
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.
            color (boolean): find the image in color screen
        Returns:
            Region: region object containing the location and size of the image
        """
        template = cv2.imread('assets/{}.png'.format(image), cv2.IMREAD_COLOR)
        match = cv2.matchTemplate(cls.screen, template, cv2.TM_CCOEFF_NORMED)

        height, width = template.shape[:2]
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            return Region(location[0], location[1], width, height)
        return None

    @classmethod
    def find_and_touch(cls, image, similarity=DEFAULT_SIMILARITY):
        """Finds the image on the screen and touches it if it exists
        Args:
            image (string): Name of the image.
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.
            color (boolean): find the image in color screen
        Returns:
            bool: True if the image was found and touched, false otherwise
        """
        region = cls.find(image, similarity)
        if region is not None:
            cls.touch_randomly(region)
            return True
        return False

    @staticmethod
    def _randint(min_val, max_val):
        """Method to generate a random value based on the min_val and max_val
        with a uniform distribution.
        Args:
            min_val (int): Minimum value of the random number.
            max_val (int): Maximum value of the random number.
        Returns:
            int: The generated random number
        """
        return randint(min_val, max_val)

    @classmethod
    def random_coord(cls, min_val, max_val):
        """Returns random coords.
        Args:
            min_val (int): Minimum value of the random number.
            max_val (int): Maximum value of the random number.
        Returns:
            int: The generated random number
        """
        return cls._randint(min_val, max_val)

    @classmethod
    def touch(cls, coords):
        """Sends an input command to touch the device screen at the specified
        coordinates via ADB
        Args:
            coords (array): An array containing the x and y coordinate of
                where to touch the screen
        """
        Adb.shell("input swipe {} {} {} {} {}".format(coords[0], coords[1], coords[0], coords[1], randint(50, 120)))
        cls.script_sleep()

    @classmethod
    def touch_randomly(cls, region=Region(0, 0, 1920, 1080)):
        """Touches a random coordinate in the specified region
        Args:
            region (Region, optional): Defaults to Region(0, 0, 1280, 720).
                specified region in which to randomly touch the screen
        """
        x = cls.random_coord(region.x, region.x + region.w)
        y = cls.random_coord(region.y, region.y + region.h)
        cls.touch([x, y])

    @classmethod
    def touch_randomly_wait(cls, region=Region(0, 0, 1920, 1080), time=None):
        """ Touch then wait.
        """
        x = cls.random_coord(region.x, region.x + region.w)
        y = cls.random_coord(region.y, region.y + region.h)
        cls.touch([x, y])
        cls.script_sleep(time)

    @classmethod
    def swipe(cls, x1, y1, x2, y2, ms):
        """Sends an input command to swipe the device screen between the
        specified coordinates via ADB
        Args:
            x1 (int): x-coordinate to begin the swipe at.
            y1 (int): y-coordinate to begin the swipe at.
            x2 (int): x-coordinate to end the swipe at.
            y2 (int): y-coordinate to end the swipe at.
            ms (int): Duration in ms of swipe. This value shouldn't be lower than 300, better if it is higher.
        """
        Adb.shell("input swipe {} {} {} {} {}".format(x1, y1, x2, y2, ms))

    @classmethod
    def purify_swipe(cls):
        """ Handle purify swipe.
        """
        #bs = gw.getWindowsWithTitle('BlueStacks')[0]
        #if not bs.isActive: bs.activate()

        cls.script_sleep(2)
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('alt')
        pyautogui.keyDown('1')
        cls.script_sleep(0.2)
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('alt')
        pyautogui.keyUp('1')

    @classmethod
    def check_schedule(cls, event):
        """ Checks whether an event is available or not.
        """
        events = {
            'weps': [('00:30', '00:59'), ('02:30', '02:59'), ('04:30', '04:59'), ('13:30', '13:59'), ('20:30', '20:59'), ('22:30', '22:59')]
        }
        closest = 999999

        for x in events.get(event):
            s = x[0].split(':')
            e = x[1].split(':')
            c = datetime.now()
            st = datetime(c.year, c.month, c.day, int(s[0]), int(s[1]))
            et = datetime(c.year, c.month, c.day, int(e[0]), int(e[1]))

            if st < c < et:
                closest = 0
                break
            else:
                r = st - c
                if r.seconds < closest and r.seconds > 0:
                    closest = round(r.seconds / 60)
        return closest
