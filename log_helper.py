# IMPORTS
import os
import sys
import logging
from datetime import datetime
import linecache
import gc

# LOGGING CONSTANTS
LOG_FILENAME_PREFIX = r'fieldmaps_on_'

LL_DEBUG = 'DEBUG'
LL_INFO = 'INFO'
LL_WARNING = 'WARNING'
LL_ERROR = 'ERROR'
LL_CRITICAL = 'CRITICAL'

SEPARATOR_1 = '============================================================================================================'
SEPARATOR_2 = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
SEPARATOR_3 = '------------------------------------------------------------------------------------------------------------'
SEPARATOR_4 = '////////////////////////////////////////////////////////////////////////////////////////////////////////////'

PFX1 = '  >'
PFX2 = '    >'
PFX3 = '      >'


def configure(log_dir_path, log_level):
    """ Set up the logger for this project"""

    file_name = LOG_FILENAME_PREFIX + datetime.now().strftime('%Y-%m-%d__%p-%H-%M-%S') + '.log'
    file_path = os.path.join(log_dir_path, file_name)
    entry_format = '%(asctime)s %(levelname)s:%(message)s'

    if log_level == LL_DEBUG:
        logging.basicConfig(filename=file_path, filemode='w', level=logging.DEBUG, format=entry_format)
    elif log_level == LL_INFO:
        logging.basicConfig(filename=file_path, filemode='w', level=logging.INFO, format=entry_format)
    elif log_level == LL_WARNING:
        logging.basicConfig(filename=file_path, filemode='w', level=logging.WARNING, format=entry_format)
    elif log_level == LL_ERROR:
        logging.basicConfig(filename=file_path, filemode='w', level=logging.ERROR, format=entry_format)
    elif log_level == LL_CRITICAL:
        logging.basicConfig(filename=file_path, filemode='w', level=logging.CRITICAL, format=entry_format)
    else:
        logging.basicConfig(filename=file_path, filemode='w', level=logging.INFO, format=entry_format)


def log_entry(message, log_level=LL_INFO, exception=None):
    """ Print and log a message"""

    # Pad message with a single space to make things look nice
    message = ' ' + message

    if exception is not None:
        logging.exception(msg=message, exc_info=exception)
    else:
        print(message)
        if log_level == LL_DEBUG:
            logging.debug(message)
        elif log_level == LL_INFO:
            logging.info(message)
        elif log_level == LL_WARNING:
            logging.warning(message)
        elif log_level == LL_ERROR:
            logging.error(message)
        elif log_level == LL_CRITICAL:
            logging.critical(message)
        else:
            logging.info(message)


def log_arcpy_messages(gp_result):
    """ Convert arcpy Result messages and severities into log entries

    Parameters:
    - gp_result: The arcpy Result object output by an arcpy geoprocessing task.

    """

    prefix = '     GP>'   # Prefix all arcpy geoprocessing message log entries with this

    try:
        # If the gp_result object is missing, log it and get out
        if not gp_result:
            log_entry(f'{prefix} + arcpy output is invalid or doesn\'t exist.')
            return None

        # Process the gp_result information
        if gp_result.messageCount == 0:
            log_entry(f'{prefix} + no arcpy output messages.')
        else:
            # Log individual messages
            for i in range(gp_result.messageCount):
                severity_message = log_arcpy_severity(gp_result.getSeverity(i))
                msg = f'{prefix} Message {i + 1} [{severity_message}] - {gp_result.getMessage(i)}'
                log_entry(msg)

            # Log the Result status
            status_message = log_arcpy_status(gp_result.status)
            log_entry(f'{prefix} Task Status: {status_message}')

    except Exception as e:
        log_entry(message=repr(e), log_level=LL_ERROR)   # Log error without providing exception
        raise e from None


def log_arcpy_status(status_code):
    """ Converts an arcpy Result object's status code into a status message """

    if status_code == 0:
        return 'New'
    elif status_code == 1:
        return 'Submitted'
    elif status_code == 2:
        return 'Waiting'
    elif status_code == 3:
        return 'Executing'
    elif status_code == 4:
        return 'Succeeded'
    elif status_code == 5:
        return 'Failed'
    elif status_code == 6:
        return 'Timed Out'
    elif status_code == 7:
        return 'Canceling'
    elif status_code == 8:
        return 'Canceled'
    elif status_code == 9:
        return 'Deleting'
    elif status_code == 10:
        return 'Deleted'
    else:
        return 'Unknown'


def log_arcpy_severity(severity_code):
    """ Converts an arcpy Result object's severity code into a severity description"""

    if severity_code == 0:
        return 'OK'
    elif severity_code == 1:
        return 'WARN'
    elif severity_code == 2:
        return 'ERROR'
    else:
        return 'UNKNOWN'


def log_exception():
    """ Return and log exception details

    This function will be called from except blocks.  It assembles an informative error message
    and writes the message to the log.  It also returns a tuple containing exception details.

    Returns:
    - Tuple
        - [0] path to the file (e.g. c:\\temp\\some_module.py)
        - [1] name of the file (e.g. some_module.py)
        - [2] function name
        - [3] line_number
        - [4] line text
        - [5] exception type name
        - [6] exception details

    """

    exception_frame = None

    try:
        # Get the error info from sys.exc_info()
        exception_type, exception_instance, exception_frame = sys.exc_info()

        # Retrieve Module, Function, Line number, and Line text details
        if exception_frame is not None:
            file_path = exception_frame.tb_frame.f_code.co_filename     # Full .py file path
            file_name = os.path.basename(file_path)                     # .py file name
            function_name = exception_frame.tb_frame.f_code.co_name     # Function Name
            line_number = exception_frame.tb_lineno                     # Line Number
            linecache.checkcache(file_path)
            line_text = linecache.getline(file_path, line_number, exception_frame.tb_frame.f_globals).strip()
        else:
            file_path = 'unspecified file path'
            file_name = 'unspecified file name'
            function_name = 'unspecified function'
            line_number = 'unspecified line number'
            line_text = 'unspecified line text'

        # Extract exception details from the exception instance
        if exception_instance is not None:
            exception_details = repr(exception_instance).replace(r'\n', ' || ')
        else:
            exception_details = ''

        # Retrieve Fully Qualified Exception Type
        if exception_type is not None:
            if exception_type.__module__ is None or exception_type.__module__ == str.__class__.__module__:
                exception_type_name = exception_type.__name__
            else:
                exception_type_name = exception_type.__module__ + '.' + exception_type.__name__
        else:
            exception_type_name = 'unspecified exception name'

        # Assemble and log the error message
        error_message_1 = f'[1] {exception_type_name} at line {line_number} of {file_name} in the {function_name} function.'
        error_message_2 = f'[2] line {line_number}: "{line_text}"'
        error_message_3 = f'[3] details: {exception_details}'

        log_entry(error_message_1, log_level=LL_ERROR)
        log_entry(error_message_2, log_level=LL_ERROR)
        log_entry(error_message_3, log_level=LL_ERROR)

        # Return exception details
        return (file_path, file_name, function_name, line_number, line_text, exception_type_name, exception_details)

    except:
        log_entry('Error in the log_exception function...')
        raise

    finally:
        del exception_frame
        gc.collect()

