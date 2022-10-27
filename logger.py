from datetime import datetime

'''
Class to log all events in the framework
'''
class Logger():
    '''
    __init__ function. Initializes all requirements when the object is constructed
    Inputs: file_name - type: string - Description: the filename to create the log
    outputs: None
    '''
    def __init__(self, filename:str):
        self.filepath = 'logs/' + filename + '.log'
        self.logfile = open(self.filepath, 'w+')
        self.log_entry_types = {0: 'INFO', 1: 'WARNING', 2: 'ERROR'}

    '''
    log_info function. Logs an info-level event.
    Inputs: lineitem - type: string - Description: the line item to log to the log file
    Ouptuts: None
    '''
    def log_info(self, lineitem:str):
        self.logfile.write(str(datetime.now()) + ' [' + self.log_entry_types[0] + '] ' + lineitem + '\n')

    '''
    log_warning function. Logs a warning-level event.
    Inputs: lineitem - type: string - Description: the line item to log to the log file
    Ouptuts: None
    '''
    def log_warning(self, lineitem:str):
        self.logfile.write(str(datetime.now()) + ' [' + self.log_entry_types[1] + '] ' + lineitem + '\n')

    '''
    log_error function. Logs an error-level event.
    Inputs: lineitem - type: string - Description: the line item to log to the log file
    Ouptuts: None
    '''
    def log_error(self, lineitem:str):
        self.logfile.write(str(datetime.now()) + ' [' + self.log_entry_types[2] + '] ' + lineitem + '\n')

    '''
    close_logfile function. Closes the class log file.
    Inputs: None
    Ouptuts: None
    '''
    def close_logfile(self):
        self.logfile.close()
