# IMPORTS!
import sys
import os
import argparse
from timeit import default_timer as timer
import json
from collections import defaultdict
from types import SimpleNamespace
from datetime import datetime as dt, timedelta as td, timezone as tz
from datetime import time as tt, date as dd
from dotenv import load_dotenv
import arcpy
import log_helper as logh
import notification_helper as noth
import generic_helper as genh
import gdb_helper as gdbh
from data_classes import ArcSdeConnParams


__version__ = '1.0'


def main(config):

    time_start = 0
    pmsg = ''       # Message for email notification upon completion
    tld_conn = ''   # Path to connection file, to be deleted after script execution

    try:
        # Start a timer to track elapsed time
        time_start = timer()

        logh.log_entry(logh.SEPARATOR_1)
        logh.log_entry('MAIN FUNCTION')
        logh.log_entry(logh.SEPARATOR_1)

        # region PARSE CONFIG FILE

        logh.log_entry(logh.SEPARATOR_2)
        logh.log_entry('PARSE CONFIG FILE')
        logh.log_entry(logh.SEPARATOR_2)

        # MARK: Temp FGDB Section
        logh.log_entry('Temporary File Section')

        # Get the TempFgdb object
        if not hasattr(config, 'TempFgdb'):
            logh.log_entry('"TempFgdb" property not found in config file.', logh.LL_ERROR)
            raise Exception('"TempFgdb" property not found in config file.') from None

        temp_fgdb = config.TempFgdb

        # Parent Folder Path
        parent_folder = temp_fgdb.ParentFolder
        if not parent_folder:
            logh.log_entry('"ParentFolder" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"ParentFolder" property value is None or empty.') from None
        elif not os.path.isdir(parent_folder):
            logh.log_entry('"ParentFolder" property value is not a valid directory path', logh.LL_ERROR)
            raise Exception('"ParentFolder" property value is not a valid directory path') from None
        elif not os.path.isabs(parent_folder):
            parent_folder = os.path.abspath(parent_folder)

        # Parent Folder is where I want the temp file gdb to be created
        logh.log_entry(f'Parent Folder: {parent_folder}')

        # File GDB static name flag
        static_name = temp_fgdb.StaticName
        if not static_name:
            static_name = False
        else:
            static_name = True
        logh.log_entry(f'Use Static FGDB Name: {"Yes" if static_name else "No"}')

        # File GDB static name flag
        keep_prelim_objects = temp_fgdb.KeepPrelimObjects
        if not keep_prelim_objects:
            keep_prelim_objects = False
        else:
            keep_prelim_objects = True
        logh.log_entry(f'Keep Preliminary Objects: {"Yes" if keep_prelim_objects else "No"}')
        logh.log_entry(logh.SEPARATOR_3)

        # MARK: EGDB Connection File
        logh.log_entry('EGDB Connection File Section')

        # Write output to EGDB feature class (boolean)
        output_to_egdb = config.OutputToEgdb
        if not output_to_egdb:
            output_to_egdb = False
        else:
            output_to_egdb = True
        logh.log_entry(f'Output to Enterprise GDB: {"Yes" if output_to_egdb else "No"}')

        # Get the Output EGDB object
        if not hasattr(config, 'OutputEGDBConnection'):
            logh.log_entry('"OutputEGDBConnection" property not found in config file.', logh.LL_ERROR)
            raise Exception('"OutputEGDBConnection" property not found in config file.') from None

        output_egdb_connection = config.OutputEGDBConnection

        # instance
        tld_instance = output_egdb_connection.Instance
        if not tld_instance:
            logh.log_entry('"Instance" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Instance" property value is None or empty.') from None

        logh.log_entry(f'Instance: {tld_instance}')

        # db
        tld_db = output_egdb_connection.Db
        if not tld_db:
            logh.log_entry('"Db" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Db" property value is None or empty.') from None

        logh.log_entry(f'Database: {tld_db}')

        # login
        tld_login = output_egdb_connection.Login
        if not tld_login:
            logh.log_entry('"Login" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Login" property value is None or empty.') from None

        logh.log_entry(f'Login: {tld_login}')

        # password
        tld_password = output_egdb_connection.Password
        if not tld_password:
            logh.log_entry('"Password" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Password" property value is None or empty.') from None

        # MESSAGE
        pmsg += f'==================================================\n'
        pmsg += f'PROCESS PARAMETERS\n'
        pmsg += f' > Temp FGDB Parent Folder: {parent_folder}\n'
        pmsg += f' > Temp FGDB Static Name: {static_name}\n'
        pmsg += f' > Temp FGDB Keep Preliminary Objects: {keep_prelim_objects}\n'
        pmsg += f'--------------------------------------------------\n'
        pmsg += f' > Output to EGDB: {"Yes" if output_to_egdb else "No"}\n'

        if output_to_egdb:
            pmsg += f' > Destination Instance: {tld_instance}\n'
            pmsg += f' > Destination Geodatabase: {tld_db}\n'
            pmsg += f' > Destination Login: {tld_login}\n'

        # endregion

        # region TEMP FILE GEODATABASE

        logh.log_entry(logh.SEPARATOR_2)
        logh.log_entry('CONSTRUCT TEMP FILE GEODATABASE')
        logh.log_entry(logh.SEPARATOR_2)

        # Create the file geodatabase
        result_create = gdbh.create_file_gdb(folder_path=parent_folder,
                                             static_name=static_name)
        fgdb_name, fgdb_path = result_create

        logh.log_entry(f'File Geodatabase: {fgdb_path}')

        # endregion

        # region DESTINATION EGDB CONNECTION

        # If we are outputting results to EGDB...
        tld_schema = ''     # This will be the default schema of the login in the destination egdb

        if output_to_egdb:
            logh.log_entry(logh.SEPARATOR_2)
            logh.log_entry('OUTPUT GEODATABASE VALIDATION')
            logh.log_entry(logh.SEPARATOR_2)

            # Create the database connection file
            logh.log_entry('Database connection file for output geodatabase')
            tld_conn = gdbh.create_database_connection_file(instance=tld_instance,
                                                            db=tld_db,
                                                            login=tld_login,
                                                            password=tld_password,
                                                            base_name='tld_conn',
                                                            folder_path=parent_folder)

            logh.log_entry(f'Connection File: {tld_conn}')

            # Get the default schema name
            params = ArcSdeConnParams(conn_file=tld_conn)
            tld_schema = gdbh.get_default_schema(params=params)
            logh.log_entry(f'Default Schema: {tld_schema}')

        # endregion

        # region GENERAL ARCPY SETUP

        # Set the spatial references
        sr = genh.get_sr_pcs_canada_lcc_wgs84()

        # arcpy environment
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = fgdb_path
        arcpy.env.outputCoordinateSystem = sr

        # endregion

        # region CLEAN UP

        logh.log_entry(logh.SEPARATOR_2)
        logh.log_entry('CLEAN UP')
        logh.log_entry(logh.SEPARATOR_2)

        # Clear EGDB Workspace Cache
        if len(tld_conn) > 0:
            logh.log_entry('Clear Workspace Cache (Data Management)')
            gp_result = arcpy.ClearWorkspaceCache_management(in_data=tld_conn)
            logh.log_arcpy_messages(gp_result)

            # Delete connection file
            logh.log_entry('Deleting the output EGDB connection file...')
            logh.log_entry('Delete (Data Management)')
            gp_result = arcpy.Delete_management(in_data=tld_conn)
            logh.log_arcpy_messages(gp_result)

        # Delete all preliminary feature classes
        if not keep_prelim_objects:
            arcpy.env.workspace = fgdb_path

            # Put all prelim objects in one list
            del_list = []
            # del_list = all_points_fc_list + main_points_fc_list + low_accuracy_points_fc_list + orphaned_points_fc_list + track_lines_fc_list

            # Delete them!
            if len(del_list) > 0:
                logh.log_entry(f'Deleting {len(del_list)} preliminary objects...')
                logh.log_entry('Delete (Data Management)')
                gp_result = arcpy.Delete_management(in_data=del_list)
                logh.log_arcpy_messages(gp_result)

        # endregion

        pmsg += f'FIELDMAPS-ON Complete!!\n'
        pmsg += f'=================================================='

    except Exception as e:
        logh.log_exception()
        logh.log_entry(message=repr(e), log_level=logh.LL_ERROR)   # Log error without providing exception
        logh.log_entry(message='Process failed.')
        return (False, repr(e))

    else:
        # No errors thrown by main
        logh.log_entry(logh.SEPARATOR_2)
        logh.log_entry('Main Function Completed Successfully')
        return (True, pmsg)

    finally:
        # Delete connection file
        if len(tld_conn) > 0:
            logh.log_entry(f'Ensure that connection file is deleted')
            if os.path.exists(tld_conn):
                os.remove(tld_conn)
                logh.log_entry(f'File deleted')
            else:
                logh.log_entry(f'File already gone')

        # Log the elapsed time
        duration = genh.get_duration_message(timer() - time_start)
        logh.log_entry(f'Elapsed Time: {duration}')
        logh.log_entry(logh.SEPARATOR_2)


def init():
    """ Parses arguments, initializes logger, and executes main function """

    recipients = []         # list of notification email recipients
    subject = ''            # email subject line
    good_times = timer()    # Start a timer to track elapsed time
    starter = dt.now()      # Capture the initial time

    try:
        # Configure the argument parser
        parser = argparse.ArgumentParser(
            description='Field Maps data prep tool',
            usage='%(prog)s [options]',
            epilog='Have a pleasant day!',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        # POSITIONAL ARGUMENTS
        # 1> JSON config file path
        parser.add_argument('config_path', type=str,
                            help='Specify the full path of the JSON config file.')

        # 2> Log folder path
        parser.add_argument('log_path', type=str,
                            help='Specify the full path of the log directory.')

        # OPTIONAL ARGUMENTS
        # 1> Return version
        parser.add_argument(
            '-v',
            action='version',
            version='%(prog)s ' + __version__)

        # if no args provided, print help and quit
        if len(sys.argv) == 1:
            parser.print_help()
            raise Exception('No arguments provided at command line...') from None

        # Retrieve Arguments
        args = parser.parse_args()

        # Validate the log folder path
        log_dir_path = args.log_path
        if not os.path.isdir(log_dir_path):
            raise Exception(f'Log folder path invalid or does not exist: {log_dir_path}') from None
        elif not os.path.isabs(log_dir_path):
            log_dir_path = os.path.abspath(log_dir_path)

        # Configure Logging
        logh.configure(log_dir_path, logh.LL_INFO)

        # Get the log file started
        logh.log_entry(logh.SEPARATOR_1)
        logh.log_entry('INIT FUNCTION')
        logh.log_entry(logh.SEPARATOR_1)

        # Validate the JSON config file path
        config_file_path = args.config_path
        if not os.path.exists(config_file_path):
            logh.log_entry(f'Config File does not exist at: {config_file_path}', logh.LL_ERROR)
            raise Exception(f'Config file does not exist at {config_file_path}') from None
        elif not os.path.isabs(config_file_path):
            config_file_path = os.path.abspath(config_file_path)

        # Test for openable, parsable JSON config file
        # 1> confirm I can open config file
        logh.log_entry(f'Config File: {config_file_path}')
        try:
            with open(config_file_path) as f:
                logh.log_entry(f'{logh.PFX1} opened...')
        except:
            logh.log_entry('Unable to open config file', logh.LL_ERROR)
            raise Exception(f'Unable to open config file at {config_file_path}') from None

        # 2> confirm I can parse contents as JSON. Also, parse it (while excluding comments) :)
        try:
            with open(config_file_path) as f:
                jsondata = ''.join(line for line in f if not line.strip().startswith('//'))     # remove comments
                config = json.loads(jsondata, object_hook=lambda d: SimpleNamespace(**d))       # parse the json
                logh.log_entry(f'{logh.PFX1} parsed...')
        except:
            logh.log_entry('Unable to parse config file into valid JSON', logh.LL_ERROR)
            raise Exception('Unable to parse config file into valid JSON') from None

        # Validate Email Details
        logh.log_entry('Email Notifications')

        if hasattr(config, 'Email'):
            email = config.Email

            if hasattr(email, 'Recipients'):
                recipients = email.Recipients
                if not recipients:
                    recipients = []    # empty list
                elif not isinstance(recipients, list):
                    recipients = []    # empty list
            else:
                logh.log_entry('Email.Recipients: Key not found.', logh.LL_ERROR)
                raise Exception('Email.Recipients: Key not found') from None

            if hasattr(email, 'Subject'):
                subject = email.Subject
                if not subject:
                    subject = 'no subject provided.'
            else:
                logh.log_entry('Email.Subject: Key not found.', logh.LL_ERROR)
                raise Exception('Email.Subject: Key not found') from None
        else:
            logh.log_entry(f'{logh.PFX3} Email: Key not found.', logh.LL_ERROR)
            raise Exception('Email: Key not found') from None

        logh.log_entry(f'{logh.PFX1} Subject: {subject}')
        logh.log_entry(f'{logh.PFX1} Recipients:')
        if len(recipients) > 0:
            for recipient in recipients:
                logh.log_entry(f'{logh.PFX3} {recipient}')
        else:
            logh.log_entry(f'{logh.PFX3} no recipients')

        # LOADING VARIABLES FROM ENV FILE
        logh.log_entry(f'Loading environment variables...')
        load_dotenv()

        logh.log_entry(f'Starting main function...')

        # EXECUTE MAIN
        result = main(config)

        success = result[0]
        return_str = result[1]

    except Exception as ex:
        success = False
        return_str = str(ex)

    logh.log_entry(logh.SEPARATOR_1)
    logh.log_entry('WRAP UP AND NOTIFICATION')
    logh.log_entry(logh.SEPARATOR_1)

    logh.log_entry(f'Main Process Outcome: {"Success" if success else "Something went wrong..."}')
    logh.log_entry(logh.SEPARATOR_3)

    # MARK: Notification
    try:
        logh.log_entry('Constructing Email Body...')

        # Log the elapsed time
        duration = genh.get_duration_message(timer() - good_times)

        # Construct email body
        body = (f'USER: {os.getlogin()}\n'
                f'START: {starter.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'END: {dt.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'DURATION: {duration}\n'
                f'OUTCOME: {"SUCCESS" if success else "FAIL :("}\n'
                f'DETAILS:\n{return_str}')


        logh.log_entry('Calling send_email_notification Method...')
        noth.send_email_notification(success=success,
                                     recipients=recipients,
                                     subject=subject,
                                     body=body)
        
        logh.log_entry(logh.SEPARATOR_1)
        logh.log_entry('FIELD MAPS DATAPREP TOOL IS DONE')
        logh.log_entry(logh.SEPARATOR_1)

    except Exception as ex:
        logh.log_entry(message=repr(ex), log_level=logh.LL_ERROR)
        logh.log_entry(message='Error in Notification Process.')


if __name__ == '__main__':
    init()
