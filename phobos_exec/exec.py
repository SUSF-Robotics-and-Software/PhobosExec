'''
Main python module for the PhobosExec module.
'''
from datetime import datetime
import time
import sys
import os
import os.path
import subprocess
import pprint

from logger import Logger
from script_interpreter import ScriptInterpreter
from archive_manager import ArchiveManager
from cmd_handlers import *

import LocomotionControl.loco_ctrl as LocoCtrl

class PhobosExec:
    '''
    Main class of the executive.
    '''

    cmd_handler_map = {
        'NONE': cmd_none,
        'SAFE': cmd_safe,
        'UNSAFE': cmd_unsafe,
        'MNVR': cmd_mnvr
    }

    def __init__(self, script_path):
        '''
        Initialise the exec.

        `script_path` - The path to the `.rps` script to run, or `None` to use
                        the comms system
        '''

        # ---------------------------------------------------------------------
        # STARTUP LOGGING SERVICE
        # ---------------------------------------------------------------------

        # Start by generating the timestamp for this session
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create the session directory
        self.session_path = create_session_dir(self.timestamp)
        if not self.session_path:
            print('Error creating the session directory - cannot continue!')

        # Now set the logger up to handle all calls from print, and redirect
        # errors into stdout so they show up in the log file.
        sys.stdout = Logger(self.session_path)
        sys.stderr = sys.stdout

        print(f'{"-"*80}\n')
        print('PhobosExec\n')
        print(f'Session ID: {self.timestamp}')
        print(f'Session directory: {self.session_path}')

        # Get uname info - machine name, kernel version etc.
        uname_output = subprocess.run(['uname', '-a'], 
                                      stdout=subprocess.PIPE,
                                      universal_newlines=True)
        print(f'Running on: {uname_output.stdout}')

        print(f'\n{"-"*80}\n')

        # Prety printer for printing the parameters
        self.pp = pprint.PrettyPrinter(indent=4)

        # ---------------------------------------------------------------------
        # LOAD SCRIPT IF NECESSARY
        # ---------------------------------------------------------------------

        if script_path:
            print('Script path found, initialising the interpreter')
            self.script = ScriptInterpreter(script_path)
        else:
            print('No script path found')
            self.script = None

        print(f'\n{"-"*80}\n')

        # ---------------------------------------------------------------------
        # INITIALISE MODULES
        # ---------------------------------------------------------------------

        print('Initialising modules...\n')

        # TODO: Init comms module here, before we touch anything that might make
        # the rover move.
        # TODO: Should we still init comms if we're running a script?

        # Init LocoCtrl
        print('LocomotionControl... ', end='')
        self.loco_ctrl = LocoCtrl.LocoCtrl()
        print('done')
        print('LocomotionControl.params: ')
        self.pp.pprint(self.loco_ctrl.params.raw)

        # TODO: Init electronics driver here (or maybe this will be done in
        # LocoCtrl?)

        # TODO: Init Autonomy modules here

        # ---------------------------------------------------------------------
        # CREATE ARCHIVES
        # ---------------------------------------------------------------------

        arch_create_funcs = [self.loco_ctrl.create_arch]
        arch_write_funcs = [self.loco_ctrl.write_arch]
        arch_close_funcs = [self.loco_ctrl.close_arch]

        self.arch_mgr = ArchiveManager(self.session_path,
                                       arch_create_funcs,
                                       arch_write_funcs,
                                       arch_close_funcs)

        # ---------------------------------------------------------------------
        # SET MAIN LOOP VARIABLES
        # ---------------------------------------------------------------------

        self.run = True
        self.ret_s = 0.0

    def main_loop(self):
        '''
        Run the main loop of the executive, this function will not exit until
        the executive is supposed to stop running
        '''

        # ---------------------------------------------------------------------
        # MAIN LOOP
        # ---------------------------------------------------------------------

        # The main loop should run at 100 Hz, this is arbitrary and could be
        # changed

        print(f'\n{"-"*80}\n')
        print('Starting main loop')

        while self.run:

            cycle_start = datetime.now()

            # If running a script file
            if self.script:
                # Get the pending scripted commands
                for cmd in self.script.get_pending(self.ret_s):

                    # If the end of the script file set running to false
                    if cmd is None:
                        print('\nEnd of script reached')
                        self.run = False
                    else:
                        # Branch based on command type:
                        handler = self.cmd_handler_map.get(cmd['type']) # pylint: disable=unsubscriptable-object

                        if handler:
                            print(f'\n{self.ret_s:.2f}: new command: {cmd}')

                            result = handler(self, cmd)
                        else:
                            print(f'Unkown command type "{cmd["type"]}", ' \
                                   'making safe') # pylint: disable=unsubscriptable-object
                            result = cmd_safe(self, cmd)

                        if not result:
                            print('Error executing last command, making safe')
                            cmd_safe(self, cmd)
            # Or if waiting for commands
            else:
                # TODO: handle comms here, for now just quit since nothing to do
                print('Can only run with script files right now')
                self.run = False

            # Write archives
            self.arch_mgr.write(self.ret_s)

            # Sync cycles
            cycle_time_s = (datetime.now() - cycle_start).total_seconds()
            sleep_duration_s = 0.01 - cycle_time_s # 100 Hz = 0.01 seconds
            if sleep_duration_s > 0.0:
                time.sleep(sleep_duration_s)
            else:
                print('Cycle overrun')

            # Increment elapsed time based on the current time after the sleep,
            # so that the elapsed time clock doesn't drift too much compared to
            # real time
            self.ret_s = self.ret_s \
                       + (datetime.now() - cycle_start).total_seconds()

        print(f'Execution stopped, rover elapsed time = {self.ret_s:.2f} s')

        # Close archives
        self.arch_mgr.close()

def create_session_dir(session_id):
    '''
    Create the session directory to store all data from the execution, including
    archives, logs, and any images.
    '''

    # ---- FIND SESSIONS FOLDER ----
    # To do this we get the current working directory, look for 'PhobosExec',
    # then go from that directory into 'sessions'

    current_path = os.getcwd()

    root_path = current_path.split('PhobosExec', 1)[0]

    session_path = os.path.join(root_path, 'PhobosExec', 'sessions', session_id)

    # Create session directory
    try:
        os.mkdir(session_path)
    except FileExistsError:
        print(f'A session with this ID has already been found at {session_path}.')
        return False
    except:
        print('An unknown error occured while creating the session directory '
              f'at {session_path}')

    # Create other directories
    archives_path = os.path.join(session_path, 'Archives')
    data_path = os.path.join(session_path, 'Data')

    try:
        os.mkdir(archives_path)
        os.mkdir(data_path)
    except:
        print('An error occured while making the subdirectories for the session.')
        return False

    return session_path
