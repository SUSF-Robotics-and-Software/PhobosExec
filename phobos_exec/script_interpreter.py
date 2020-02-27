import re
import json
from collections import deque

class ScriptInterpreter:

    def __init__(self, script_path):
        '''
        Load the script from the given path and parse it.
        '''
        self.script_path = script_path

        self.pending = deque()
        self.executed = []
        
        # Read the script file
        with open(script_path) as f:
            script_str = f.read()
        
        # Run the regex to find all matching commands, the magic regex pattern:
        #
        #   ^\s*(\d+(\.\d+)?)\s*:\s*([^;]*);
        #
        # First matches a line with any amount of leading whitespace. Then it 
        # looks for a properly formatted time (integer or decimal), then more 
        # optional whitespace before a colon. After the colon any character 
        # except semicolons are allowed, this is where the JSON goes. Finally we
        # match a semicolon to end the command
        cmd_matches = re.findall(r'^\s*(\d+(\.\d+)?)\s*:\s*([^;]*);', 
                                 script_str, flags=re.MULTILINE)

        # Loop through all matches adding them to the exec timeline
        for match in cmd_matches:
            exec_time_s = float(match[0])

            # Convert the JSON payload
            try:
                cmd_json = json.loads(match[2])
            except ValueError as e:
                print(f'Invalid command at t={exec_time_s}:')
                raise(e)

            self.pending.append((exec_time_s, cmd_json))

        # Print some info on the script
        print(f'Loaded {len(self.pending)} commands from {script_path}')
        print(f'Total script run time is {self.pending[-1][0]} s')

    def get_pending(self, ret_s):
        '''
        Get the list of pending commands to be executed at this time.

        This will return a list of all commands which haven't been executed whos
        exec times are lower than the current value of the rover elapsed time.

        Usage:
        ```
        for cmd in script.get_pending(ret_s):
            if cmd is None:
                # The script has ended now, you should exit
            else:
                # Handle commands
        ```
        '''

        # Return the EOS message if the pending queue is empty
        if len(self.pending) == 0:
            return [None]
        
        pending_cmds = []

        # While the exec time of the command at the front of the queue is less
        # than the current time
        while self.pending[0][0] < ret_s:
            cmd_item = self.pending.popleft()
            pending_cmds.append(cmd_item[1])

            # Add the item to the executed queue
            self.executed.append(cmd_item)

            # Check if we've just poped the last item
            if len(self.pending) == 0:
                break

        return pending_cmds