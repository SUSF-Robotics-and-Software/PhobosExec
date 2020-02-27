import sys
import os.path

class Logger(object):
    """
    Small simple logger object which duplicates print messages to both stdout
    and to a log file named 'PhobosExec.log' in the specified session path.

    Before any `print` calls you should do:
    ```
    sys.stdout = Logger("PATH/TO/SESSION")
    ```
    """
    def __init__(self, session_path):
        self.terminal = sys.stdout
        log_path = os.path.join(session_path, 'PhobosExec.log')
        self.log = open(log_path, 'w+')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # TODO: Do we need to do anything here?
        pass