'''
Holds the archive manager.
'''
import os.path

class ArchiveManager:
    '''
    Manage archiving. This will log all data in the system on every call of
    `ArchiveManager.write`.
    '''

    def __init__(self, session_path, arch_create_funcs, arch_write_funcs, arch_close_funcs):
        '''
        Initialise the archive manager, and create the files used to save each
        module's data.

        Inputs:
        * `session_path` - Path to the current session's root directory
        * `arch_create_funcs` - Dictionary of each module's `.create_arch`
            function. Keys in this dict must match the name of the instance of
            the module stored in the `phobos_exec` class, i.e. for a
            LocomotionControl instance named `loco_ctrl`, its entry should be
            `{'loco_ctrl': self.loco_ctrl.create_arch}`.
        * `arch_write_funcs` - Dictionary of each module's `.write_arch`
            function. Keys in this dict must match the name of the instance of
            the module stored in the `phobos_exec` class, i.e. for a
            LocomotionControl instance named `loco_ctrl`, its entry should be
            `{'loco_ctrl': self.loco_ctrl.write_arch}`.
        '''
        self.archive_path = os.path.join(session_path, 'Archives')

        self.arch_create_funcs = arch_create_funcs
        self.arch_write_funcs = arch_write_funcs
        self.arch_close_funcs = arch_close_funcs

        for create_func in self.arch_create_funcs:
            create_func(self.archive_path)

    def write(self, ret_s):
        '''
        Write out all archives of the exec state.
        '''

        for write_func in self.arch_write_funcs:
            write_func(ret_s)

    def close(self):
        '''
        Close all open archive files
        '''

        for close_func in self.arch_close_funcs:
            close_func()