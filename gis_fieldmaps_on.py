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
from data_classes import ArcSdeConnParams, FeatureClassObj


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

        # Validate Only flag (boolean)
        validate_only = config.ValidateOnly
        if not validate_only:
            validate_only = False
        else:
            validate_only = True
        logh.log_entry(f'Validate Only: {"Yes" if validate_only else "No"}')

        # Get the Output EGDB object
        if not hasattr(config, 'EGDBConnection'):
            logh.log_entry('"EGDBConnection" property not found in config file.', logh.LL_ERROR)
            raise Exception('"EGDBConnection" property not found in config file.') from None

        egdb_connection = config.EGDBConnection

        # instance
        tld_instance = egdb_connection.Instance
        if not tld_instance:
            logh.log_entry('"Instance" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Instance" property value is None or empty.') from None

        logh.log_entry(f'Instance: {tld_instance}')

        # db
        tld_db = egdb_connection.Db
        if not tld_db:
            logh.log_entry('"Db" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Db" property value is None or empty.') from None

        logh.log_entry(f'Database: {tld_db}')

        # login
        tld_login = egdb_connection.Login
        if not tld_login:
            logh.log_entry('"Login" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Login" property value is None or empty.') from None

        logh.log_entry(f'Login: {tld_login}')

        # password
        tld_password = egdb_connection.Password
        if not tld_password:
            logh.log_entry('"Password" property value is None or empty.', logh.LL_ERROR)
            raise Exception('"Password" property value is None or empty.') from None

        # MARK: Default Field Names
        # Get the KeyFields object
        if not hasattr(config, 'KeyFields'):
            logh.log_entry('"KeyFields" property not found in config file.', logh.LL_ERROR)
            raise Exception('"KeyFields" property not found in config file.') from None

        logh.log_entry('getting KeyFields')
        key_fields = config.KeyFields
        keyfld_area_ha: str|None = getattr(key_fields, genh.KeyFieldType.AREA_HA.value, None)
        keyfld_area_ac: str|None = getattr(key_fields, genh.KeyFieldType.AREA_AC.value, None)
        keyfld_length_m: str|None = getattr(key_fields, genh.KeyFieldType.LENGTH_M.value, None)
        keyfld_easting: str|None = getattr(key_fields, genh.KeyFieldType.EASTING.value, None)
        keyfld_northing: str|None = getattr(key_fields, genh.KeyFieldType.NORTHING.value, None)
        keyfld_zone: str|None = getattr(key_fields, genh.KeyFieldType.ZONE.value, None)

        logh.log_entry(f'Key Fields')
        logh.log_entry(f' {genh.KeyFieldType.AREA_HA.name}: {keyfld_area_ha}')
        logh.log_entry(f' {genh.KeyFieldType.AREA_AC.name}: {keyfld_area_ac}')
        logh.log_entry(f' {genh.KeyFieldType.LENGTH_M.name}: {keyfld_length_m}')
        logh.log_entry(f' {genh.KeyFieldType.EASTING.name}: {keyfld_easting}')
        logh.log_entry(f' {genh.KeyFieldType.NORTHING.name}: {keyfld_northing}')
        logh.log_entry(f' {genh.KeyFieldType.ZONE.name}: {keyfld_zone}')

        # MARK: Feature Class List
        logh.log_entry('Feature Classes')

        # Get the FeatureClasses object
        if not hasattr(config, 'FeatureClasses'):
            logh.log_entry('"FeatureClasses" property not found in config file.', logh.LL_ERROR)
            raise Exception('"FeatureClasses" property not found in config file.') from None

        feature_class_entries: list[str] = config.FeatureClasses
        if not feature_class_entries:
            logh.log_entry('"FeatureClasses" is nothing (how is this even possible?)', logh.LL_ERROR)
            raise Exception('"FeatureClasses" is nothing (how is this even possible?)') from None
        elif not isinstance(feature_class_entries, list):
            logh.log_entry('"FeatureClasses" is not a list', logh.LL_ERROR)
            raise Exception('"FeatureClasses" is not a list') from None
        elif len(feature_class_entries) == 0:
            logh.log_entry('"FeatureClasses" list must have at least one entry!', logh.LL_ERROR)
            raise Exception('"FeatureClasses" list must have at least one entry!') from None
        else:
            logh.log_entry(f'"FeatureClasses" list count: {len(feature_class_entries)}')

        # MESSAGE
        pmsg += f'==================================================\n'
        pmsg += f'PROCESS PARAMETERS\n'
        pmsg += f' > Temp FGDB Parent Folder: {parent_folder}\n'
        pmsg += f' > Temp FGDB Static Name: {static_name}\n'
        pmsg += f' > Temp FGDB Keep Preliminary Objects: {keep_prelim_objects}\n'
        pmsg += f' > Validate Only: {"Yes" if validate_only else "No"}\n'
        pmsg += f'--------------------------------------------------\n'
        pmsg += f' > Server Instance: {tld_instance}\n'
        pmsg += f' > Enterprise Geodatabase: {tld_db}\n'
        pmsg += f' > Login: {tld_login}\n'
        pmsg += f'--------------------------------------------------\n'
        pmsg += f'KEY FIELDS\n'
        pmsg += f' > {genh.KeyFieldType.AREA_HA.name}: {keyfld_area_ha or "<not found or provided>"}\n'
        pmsg += f' > {genh.KeyFieldType.AREA_AC.name}: {keyfld_area_ac or "<not found or provided>"}\n'
        pmsg += f' > {genh.KeyFieldType.LENGTH_M.name}: {keyfld_length_m or "<not found or provided>"}\n'
        pmsg += f' > {genh.KeyFieldType.EASTING.name}: {keyfld_easting or "<not found or provided>"}\n'
        pmsg += f' > {genh.KeyFieldType.NORTHING.name}: {keyfld_northing or "<not found or provided>"}\n'
        pmsg += f' > {genh.KeyFieldType.ZONE.name}: {keyfld_zone or "<not found or provided>"}\n'
        pmsg += f'--------------------------------------------------\n'
        pmsg += f'FEATURE CLASSES\n'

        for feature_class_entry in feature_class_entries:
            pmsg += f' >   {feature_class_entry}\n'

        pmsg += f'==================================================\n'

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

        # region EGDB CONNECTION

        # This will be the default schema of the egdb login
        tld_schema = ''     

        logh.log_entry(logh.SEPARATOR_2)
        logh.log_entry('GEODATABASE VALIDATION')
        logh.log_entry(logh.SEPARATOR_2)

        # Create the database connection file
        logh.log_entry('Database connection file for geodatabase')
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

        # region FEATURE CLASS VALIDATION

        # MARK: Validate Feature Classes
        arcpy.env.workspace = tld_conn

        dict_feature_classes: dict[str, FeatureClassObj] = {}
        other_entries: list[str] = []
        missing_entries: list[str] = []

        # Eliminate duplicate entries
        feature_class_entries = list(set(feature_class_entries))
        feature_class_entries.sort()

        for feature_class_entry in feature_class_entries:
            if arcpy.Exists(feature_class_entry):
                descr = arcpy.Describe(feature_class_entry)
                if descr.dataType.lower() == 'featureclass':
                    dict_feature_classes[feature_class_entry] = FeatureClassObj(name=feature_class_entry, shape_type=descr.shapeType)
                else:
                    other_entries.append(feature_class_entry)
            else:
                missing_entries.append(feature_class_entry)

        logh.log_entry('Feature Classes:')
        for (feature_class_entry, fc_obj) in dict_feature_classes.items():
            logh.log_entry(f'fc: {feature_class_entry}   Shape type: {fc_obj.shape_type}')
        logh.log_entry('Other Entries:')
        for oe in other_entries:
            logh.log_entry(oe)
        logh.log_entry('Missing Entries:')
        for me in missing_entries:
            logh.log_entry(me)

        if len(dict_feature_classes) == 0:
            logh.log_entry('No valid feature classes found in list of entries.', logh.LL_ERROR)
            raise Exception('No valid feature classes found in list of entries.') from None

        # Cursor
        # with arcpy.da.SearchCursor('ITGEO_GEN.blueberry', '*') as cursor:
        #     for row in cursor:
        #         logh.log_entry(f'row: {row[2]}')
        #     del cursor

        # Fields
        # for a in arcpy.ListFields(dataset='ITGEO_GEN.blueberry'):
        #     logh.log_entry(f'name: {a.name}')

        # # Set the spatial references
        # sr = genh.get_sr_pcs_canada_lcc_wgs84()

        # # arcpy environment
        # arcpy.env.overwriteOutput = True
        # arcpy.env.workspace = fgdb_path
        # arcpy.env.outputCoordinateSystem = sr



        # endregion

        # region DO THE THING

        # What I need to do here:
        # 1. For each feature in each feature class:
        #   - Retrieve UTM Easting, Northing, and Zone for each feature's centroid
        #   - Calculate area for each polygon feature
        #   - Calculate length for each line feature

        # Divvy up into point, line, and polygon groups
        fc_all: list[FeatureClassObj] = [fc_obj for fc_obj in dict_feature_classes.values()]
        fc_points: list[FeatureClassObj] = [fc_obj for fc_obj in dict_feature_classes.values() if fc_obj.shape_type.lower() == genh.ShapeType.POINT.value]
        fc_polylines: list[FeatureClassObj] = [fc_obj for fc_obj in dict_feature_classes.values() if fc_obj.shape_type.lower() == genh.ShapeType.POLYLINE.value]
        fc_polygons: list[FeatureClassObj] = [fc_obj for fc_obj in dict_feature_classes.values() if fc_obj.shape_type.lower() == genh.ShapeType.POLYGON.value]


        logh.log_entry('ALL FCS:')
        for fc in fc_all:
            logh.log_entry(f' > {fc.name}')
        logh.log_entry('POINT FCS:')
        for fc_point in fc_points:
            logh.log_entry(f' > {fc_point.name}')
        logh.log_entry('POLYLINE FCS:')
        for fc_polyline in fc_polylines:
            logh.log_entry(f' > {fc_polyline.name}')
        logh.log_entry('POLYGON FCS:')
        for fc_polygon in fc_polygons:
            logh.log_entry(f' > {fc_polygon.name}')

        # Establish existence of key fields
        if keyfld_area_ha is not None:
            for fc_obj in fc_all:
                for fld in arcpy.ListFields(dataset=fc_obj.name):
                    if fld.name.lower() == keyfld_area_ha.lower():
                        fc_obj.has_area_ha = True
                        fc_obj.fld_area_ha = fld.name
        if keyfld_area_ac is not None:
            for fc_obj in fc_all:
                for fld in arcpy.ListFields(dataset=fc_obj.name):
                    if fld.name.lower() == keyfld_area_ac.lower():
                        fc_obj.has_area_ac = True
                        fc_obj.fld_area_ac = fld.name
        if keyfld_length_m is not None:
            for fc_obj in fc_all:
                for fld in arcpy.ListFields(dataset=fc_obj.name):
                    if fld.name.lower() == keyfld_length_m.lower():
                        fc_obj.has_length_m = True
                        fc_obj.fld_length_m = fld.name
        if keyfld_easting is not None:
            for fc_obj in fc_all:
                for fld in arcpy.ListFields(dataset=fc_obj.name):
                    if fld.name.lower() == keyfld_easting.lower():
                        fc_obj.has_easting = True
                        fc_obj.fld_easting = fld.name
        if keyfld_northing is not None:
            for fc_obj in fc_all:
                for fld in arcpy.ListFields(dataset=fc_obj.name):
                    if fld.name.lower() == keyfld_northing.lower():
                        fc_obj.has_northing = True
                        fc_obj.fld_northing = fld.name
        if keyfld_zone is not None:
            for fc_obj in fc_all:
                for fld in arcpy.ListFields(dataset=fc_obj.name):
                    if fld.name.lower() == keyfld_zone.lower():
                        fc_obj.has_zone = True
                        fc_obj.fld_zone = fld.name

        for fc_obj in fc_all:
            logh.log_entry(f'FC: {fc_obj.name}')
            logh.log_entry(f'  > {genh.KeyFieldType.AREA_HA.name}: {fc_obj.has_area_ha}  ---  {fc_obj.fld_area_ha}')
            logh.log_entry(f'  > {genh.KeyFieldType.AREA_AC.name}: {fc_obj.has_area_ac}  ---  {fc_obj.fld_area_ac}')
            logh.log_entry(f'  > {genh.KeyFieldType.LENGTH_M.name}: {fc_obj.has_length_m}  ---  {fc_obj.fld_length_m}')
            logh.log_entry(f'  > {genh.KeyFieldType.EASTING.name}: {fc_obj.has_easting}  ---  {fc_obj.fld_easting}')
            logh.log_entry(f'  > {genh.KeyFieldType.NORTHING.name}: {fc_obj.has_northing}  ---  {fc_obj.fld_northing}')
            logh.log_entry(f'  > {genh.KeyFieldType.ZONE.name}: {fc_obj.has_zone}  ---  {fc_obj.fld_zone}')


        # Now for each FC, for each feature, retrieve a centroid point in WGS84
        sr = genh.get_sr_gcs_wgs84()
        for fc_obj in fc_points:
            if fc_obj.name.lower() == 'ITGEO_GEN.MWO_AnthroPoint'.lower():

                with arcpy.da.SearchCursor(in_table=fc_obj.name,
                                           field_names='SHAPE@XY',
                                           spatial_reference=sr) as cursor:
                    for row in cursor:
                        # TODO: Check for None values from the shape token = null geometry
                        wgs84_x, wgs84_y = row[0]

                        if wgs84_x is not None:
                            # Get the zone
                            # TODO: Make this more robust (if longitude is not between 0 and -180)
                            z = ((wgs84_x + 180)//6) + 1

                            # Get the easting and northing
                            epsg = 32600 + z
                            utm_sr = arcpy.SpatialReference(epsg)
                            # TODO: I'm here!!!
                            # Construct a point geometry object
                            # RETRIEVE the transformation so I can project the point geometry object





                del cursor
        # # Open the search cursor
        # logh.log_entry('Opening cursor on track points source...')
        # fields = [
        #     TrackPointClass.fld_created_user[0],
        #     TrackPointClass.fld_full_name[0],
        #     TrackPointClass.fld_location_timestamp[0]
        # ]

        # with arcpy.da.SearchCursor(in_table=tps_conn,
        #                            field_names=fields,
        #                            sql_clause = (None, f'ORDER BY {TrackPointClass.fld_created_user[0]}')) as cursor:
        #     for row in cursor:
        #         user = row[0]                   # user
        #         full_name = row[1]              # full name
        #         location_timestamp = row[2]     # stamp

        #         # If the user isn't in the dictionary yet, add an entry
        #         if user not in track_users:
        #             uc_object = UserClass(user=user,
        #                                   user_id=0,
        #                                   full_name=full_name,
        #                                   earliest_timestamp=location_timestamp,
        #                                   latest_timestamp=location_timestamp,
        #                                   points_all=1,
        #                                   points_low_accuracy=0,
        #                                   points_deleted_dupes=0,
        #                                   points_orphan=0,
        #                                   points_line=0,
        #                                   line_count=0)

        #             track_users[user] = uc_object

        #         # User already exists in the dictionary - update some values                    
        #         else:
        #             uc_object = track_users[user]
        #             uc_object.points_all += 1
        #             if location_timestamp < uc_object.earliest_timestamp:
        #                 uc_object.earliest_timestamp = location_timestamp
        #             if location_timestamp > uc_object.latest_timestamp:
        #                 uc_object.latest_timestamp = location_timestamp
        # del cursor




        # Check for default fields in each feature class
        # # Standard area field names used across most polygon layers
        # FIELD_AREA_HA  = "UTM_Ha"   # geodesic hectares
        # FIELD_AREA_AC  = "UTM_Ac"   # international acres (converted from Ha)
        # INTERNATIONAL_ACRES_PER_HA = 2.471053814671653

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
