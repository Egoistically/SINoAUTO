from util.logger import Logger
from util.adb import Adb
from util.utils import Utils, Region
from datetime import datetime, timedelta
from threading import Thread
import sys

class SINoAUTO(object):
    """ Main stuff.
    """

    def __init__(self, event: str, diff: str = None, nightmare: int = 0, debug: bool = False):
        """ Initializes stuff.
        """
        self.region = {
            'btn_nightmare_1th': Region(110, 1657, 51, 51),
            'btn_nightmare_2th': Region(314, 1657, 51, 51),
            'btn_nightmare_3th': Region(515, 1657, 51, 51),
            'btn_nightmare_4th': Region(715, 1657, 51, 51),
            'btn_nightmare_5th': Region(925, 1661, 51, 51),

            'btn_home': Region(44, 1803, 70, 70),
            'btn_reconnect': Region(682, 1771, 75, 70),
            'btn_first_skill': Region(102, 1752, 60, 16),
            'btn_close_alert': Region(486, 1777, 105, 35),

            'btn_purify': Region(926, 323, 90, 90),
            'purify_ok_begin': Region(659, 1766, 120, 60),
            'purify_ok_result': Region(480, 1798, 120, 60),

            'btn_story': Region(202, 1806, 60, 60),
            'btn_summon_menu': Region(89, 1502, 90, 30),
            'btn_summon': Region(629, 1283, 160, 39),
            'btn_deck_reload': Region(490, 1666, 100, 50),
            'story_coop': Region(214, 890, 70, 70),
            'story_events': Region(788, 890, 70, 70),
            'story_main': Region(454, 1235, 172, 103),
            'story_start_combat': Region(478, 1607, 125, 50),
            'story_ok': Region(509, 1778, 73, 43)
        }
        self.event = event
        self.diff = diff
        self.combat_event = {}
        self.use_nightmare = nightmare

        self.combat_done = 0
        self.next_combat = datetime.now()
        self.next_purification = None

        if debug:
            Logger.enable_debugging(Logger)

    def run_purification(self):
        """ Handles purification
        """
        Utils.touch_randomly(self.region['btn_purify'])
        Utils.script_sleep(2)
        Utils.touch_randomly(self.region['purify_ok_begin'])
        Utils.script_sleep(2)

        Utils.purify_swipe()
        while True:
            Utils.update_screen()
            #Utils.find_and_touch('purification/arrow', 0.8)

            if Utils.find('menu/result'):
                Utils.script_sleep(10)
                Utils.touch_randomly_wait(self.region['purify_ok_result'], 2)
                Utils.touch_randomly_wait(self.region['purify_ok_result'], 2)
                Utils.touch_randomly_wait(self.region['btn_home'], 1)
                break

        Utils.wait_update_screen(3)
        self.nav_menu('home')

        Utils.script_sleep(5)
        self.next_combat = datetime.now()
        self.next_purification = datetime.now() + timedelta(hours=4)
        return

    def nav_menu(self, menu: str, delay: int = 0):
        Utils.wait_update_screen(1)

        while not Utils.find('menu/{}'.format(menu), 0.98):
            if Utils.find('menu/update'):
                self.handle_reconnect()
                Utils.update_screen()
            elif Utils.find_and_touch('menu/button_ok', 0.98):
                Utils.script_sleep(1)
            else:
                Utils.touch_randomly(self.region['btn_{}'.format(menu)])
                Utils.script_sleep(2)
            Utils.update_screen()

        Utils.script_sleep(delay)
        return

    def run_event(self, event, difficulty: str):
        """ Handles event combat.
        """
        self.nav_menu('story')

        if event == 'justice':
            Utils.touch_randomly(self.region['story_main'])
            Utils.wait_update_screen(2)

            Utils.swipe(100, 500, 540, 500, 300)
            Utils.script_sleep(2)
            Utils.touch_randomly(Region(373, 948, 87, 30))

            Utils.wait_update_screen(2)
            Utils.find_and_touch('difficulties/16', 0.999)
        else:
            Utils.touch_randomly(self.region['story_events'])
            Utils.wait_update_screen(2)

            while not Utils.find_and_touch(f'banners/{event}', 0.8):
                Utils.swipe(540, 835, 540, 535, 300)
                Utils.wait_update_screen(1)

            Utils.wait_update_screen(1)
            Utils.find_and_touch(f'difficulties/{difficulty}', 0.99)

        Utils.script_sleep(2)
        Utils.touch_randomly_wait(self.region['story_start_combat'], 3)

        if self.run_combat():
            Logger.log_warning('No AP left, number of runs: ' + str(self.combat_done))
            self.regen_ap()

        return

    def run_combat(self):
        """ Runs combat until no AP left.
        """
        w1 = False
        alive = True
        Logger.log_success('Starting combats.')
        while not Utils.find('menu/recover_ap'):
            Utils.wait_update_screen(1.9)

            found = self.combat_threads()
            if found['menu/wave1'] and not w1 and self.use_nightmare > 0:
                Logger.log_info("Summoning nightmare.")
                self.combat_done += 1
                Utils.touch_randomly_wait(self.region['btn_summon_menu'], 0.6)
                Utils.touch_randomly_wait(self.region['btn_nightmare_{}th'.format(self.use_nightmare)])
                Utils.wait_update_screen()
                while Utils.find_and_touch('menu/summon', 0.95):
                    Utils.update_screen()
                Utils.touch_randomly_wait(self.region['btn_summon_menu'], 0.6)
                w1 = True
            elif found['menu/wave2'] and w1 and self.use_nightmare > 0:
                w1 = False
            elif found['menu/home']:
                Logger.log_warning("Died...")
                alive = False
                break
            elif found['menu/connection_failed']:
                Logger.log_info('Server almost boomed, but not entirely.')
                Utils.touch_randomly(self.region['btn_reconnect']) #tap if disconnected
            elif found['menu/communication_failure']:
                Logger.log_warning('Server boomed, tryna reconnect.')
                self.handle_reconnect()
            elif found['menu/deck_reload']:
                Logger.log_debug('Reloading deck.')
                Utils.touch_randomly(self.region['btn_deck_reload']) #reload deck if everything's been used
            else:
                Utils.touch_randomly(self.region['btn_first_skill']) #tap first skill and retry
        return alive

    def handle_reconnect(self):
        """ Handles reconnecting to shitty servers.
        """
        Utils.touch_randomly_wait(self.region['btn_close_alert'], 5)
        Utils.touch_randomly_wait(self.region['story_ok'], 10)
        Utils.wait_update_screen(5)
        if Utils.find('menu/reconnect'):
            Utils.touch_randomly(self.region['btn_reconnect'])
            Utils.script_sleep(5)
        return

    def combat_threads(self):
        """ Multithreads stuff.
        """
        threads = []
        home = Thread(
            target=self.handle_thread, args=('menu/home',))
        twave1 = Thread(
            target=self.handle_thread, args=('menu/wave1',))
        twave2 = Thread(
            target=self.handle_thread, args=('menu/wave2',))
        tconnection_failed = Thread(
            target=self.handle_thread, args=('menu/connection_failed',))
        tcommunication_failure = Thread(
            target=self.handle_thread, args=('menu/communication_failure',))
        tdeck_reload = Thread(
            target=self.handle_thread, args=('menu/deck_reload',))
        threads.extend([home, twave1, twave2, tconnection_failed, tcommunication_failure, tdeck_reload])

        Utils.multithreader(threads)
        return self.combat_event

    def handle_thread(self, event):
        """ Handles threads.
        """
        self.combat_event[event] = (
            True
            if (Utils.find(event))
            else False)

    def regen_ap(self):
        """ Handles AP recovery message and enters standby.
        """
        Utils.touch_randomly_wait(self.region['btn_close_alert'], 2) #close alert
        Utils.update_screen()
        if Utils.find('menu/button_ok'):
            Utils.touch_randomly_wait(self.region['story_ok'], 1)
            Utils.touch_randomly_wait(self.region['story_ok'], 1)
            Utils.touch_randomly_wait(self.region['story_ok'], 3)
        Utils.touch_randomly(self.region['btn_home'])
        Utils.wait_update_screen(2)
        if Utils.find('menu/update'):
            self.handle_reconnect()
        self.next_combat = datetime.now() + timedelta(hours=1)

    def should_combat(self):
        """ Checks whether bot should combat.
        """
        return self.next_combat < datetime.now() or \
            self.next_purification and (self.next_purification - datetime.now()).seconds < 1800

Adb().init()
script = SINoAUTO(event='evolution_weapon', diff='60', nightmare=2, debug=True)

try:
    while True:
        Utils.update_screen()
        # commented stuff is broken and cba fixing it

        if Utils.find('menu/purification_available', 0.8):
            script.run_purification()
            Logger.log_success('Finished purification.')

        # elif Utils.check_schedule('weps') == 0 and script.event == 1 and script.should_combat():
        #     Logger.log_msg('Weapon event available, farming it.')
        #     script.run_event(1)

        elif script.should_combat():
            Logger.log_msg('Farming event {}.'.format(script.event))
            script.run_event(script.event, script.diff)

        # elif script.event == 1 and Utils.check_schedule('weps') > 180 \
        #     and Utils.find('menu/ap_bar_half'):
        #     Logger.log_msg('Farming event {}.'.format(alt_event))
        #     script.run_event(alt_event)

        else:
            Logger.log_info('Nothing to do, idling for 5 mins.')
            Utils.script_sleep(300)

except KeyboardInterrupt:
    sys.exit(0)