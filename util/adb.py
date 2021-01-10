import subprocess
from util.logger import Logger

class Adb(object):

    service = ''
    transID = ''
    tcp = False

    def init(self):
        """Kills and starts a new ADB server
        """
        self.kill_server()
        return self.start_server()

    def start_server(self):
        """
        Starts the ADB server and makes sure the android device (emulator) is attached.
        Returns:
            (boolean): True if everything is ready, False otherwise.
        """
        cmd = ['adb', 'start-server']
        subprocess.call(cmd)

    @staticmethod
    def kill_server():
        """Kills the ADB server
        """
        cmd = ['adb', 'kill-server']
        subprocess.call(cmd)

    @staticmethod
    def exec_out(args):
        """Executes the command via exec-out
        Args:
            args (string): Command to execute.
        Returns:
            tuple: A tuple containing stdoutdata and stderrdata
        """
        cmd = ['adb', 'exec-out'] + args.split(' ')
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        return process.communicate()[0]

    @staticmethod
    def shell(args):
        """Executes the command via adb shell
        Args:
            args (string): Command to execute.
        """
        cmd = ['adb', 'shell'] + args.split(' ')
        Logger.log_debug(str(cmd))
        subprocess.call(cmd)

    @staticmethod
    def cmd(args):
        """Executes a general command of ADB
        Args:
            args (string): Command to execute.
        """
        cmd = ['adb'] + args.split(' ')
        Logger.log_debug(str(cmd))
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        return process.communicate()[0]