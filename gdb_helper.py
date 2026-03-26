
# IMPORTS
# Python
import sys
import os
from datetime import datetime as dt

# ESRI
import arcpy

# JC
import log_helper as logh
import data_classes as dc

FILEGDB_NAME_PREFIX = 'fieldmaps_on'


def create_file_gdb(folder_path, static_name):
    """ Create a file geodatabase

    Parameters:
    - folder_path :: path to the parent directory where the file geodatabases get created.
    - static_name :: true-filegdb name does not include the date time component.  false-it does

    Return Values:
        - Tuple
            - [0] File geodatabase name
            - [1] Full path of the file geodatabase (this includes the file geodatabase name)

    """

    try:
        # Generate a new geodatabase name
        fgdb_name, fgdb_fullpath = generate_file_gdb_name(folder_path=folder_path, static_name=static_name)

        # Check if a file geodatabase already exists at that path
        if arcpy.Exists(fgdb_fullpath):
            # try to delete it
            logh.log_entry('Deleting Existing Geodatabase')
            logh.log_entry('GPTool: Delete (Data Management)')
            items_to_delete = [fgdb_fullpath]
            gp_result = arcpy.Delete_management(in_data=items_to_delete)
            logh.log_arcpy_messages(gp_result)
            logh.log_entry(f'Delete success: {gp_result.getOutput(0)}')

        # Create the file geodatabase
        logh.log_entry('Creating File Geodatabase')
        logh.log_entry('GPTool: Create File Geodatabase (Data Management)')
        gp_result = arcpy.CreateFileGDB_management(folder_path, fgdb_name)
        logh.log_arcpy_messages(gp_result)

        return (fgdb_name, fgdb_fullpath)

    except:
        logh.log_exception()
        raise Exception('Error creating the builder geodatabase.') from None


def generate_file_gdb_name(folder_path, static_name):
    """ Generate the name for a file geodatabase

    Parameters:
        - folder_path :: Path to the parent directory where the file geodatabases get created.
        - static_name :: true-filegdb name does not include the date time component.  false-it does

    Return Values:
        - Tuple (2 values)
            - [0] File geodatabase name
            - [1] Full path of the file geodatabase (this includes the file geodatabase name)

    """

    # Get the datetime based suffix
    suffix = dt.now().strftime('_%Y_%m_%d__%H_%M_%S')

    if static_name:
        gdb_name = FILEGDB_NAME_PREFIX + '.gdb'
    else:
        gdb_name = FILEGDB_NAME_PREFIX + suffix + '.gdb'


    full_path = os.path.join(folder_path, gdb_name)

    return (gdb_name, full_path)


def create_database_connection_file(instance: str,
                                    db: str,
                                    login: str,
                                    password: str,
                                    base_name: str,
                                    folder_path: str) -> str:
    """Create an ESRI database connection file (.sde) to a SQL Server database.
    """
    try:
        # Validate folder path
        if not os.path.exists(folder_path):
            raise Exception('Folder path does not exist') from None

        # Check for existing connection file
        full_name = base_name + '.sde'
        full_path = os.path.join(folder_path, full_name)

        logh.log_entry(f'Create database connection file: {full_path}')

        # Delete it if it exists!  NOTE: There may be locks here...
        if os.path.exists(full_path):
            # If the sde file exists, delete it
            logh.log_entry('File already exists')
            logh.log_entry('Deleting file...')
            os.remove(full_path)
            logh.log_entry('File deleted')

        # Create the new database connection file
        logh.log_entry('GPTool: Create Database Connection (Data Management)')
        gp_result = arcpy.CreateDatabaseConnection_management(out_folder_path=folder_path,
                                                              out_name=base_name,
                                                              database_platform='SQL_SERVER',
                                                              instance=instance,
                                                              account_authentication='DATABASE_AUTH',
                                                              username=login,
                                                              password=password,
                                                              save_user_pass='SAVE_USERNAME',
                                                              database=db)
        logh.log_arcpy_messages(gp_result)        

        return gp_result.getOutput(0)

    except:
        logh.log_exception()
        raise Exception('Error creating database connection file') from None    


def get_default_schema(params: dc.ArcSdeConnParams) -> str:
    """ Retrieve the name of the default schema for a SQL Server database user.
    """

    # The connection object
    sde_conn = None

    try:

        sql_statement = 'SELECT SCHEMA_NAME()'
        schema_name = ''

        # Retrieve the conn object
        sde_conn = get_arcsde_connection_object(params=params)

        # Retrieve the schema name
        schema_name = sde_conn.execute(sql_statement)
        return schema_name

    except:
        logh.log_exception()
        raise Exception('Error retrieving default schema') from None
    finally:
        if sde_conn:
            del sde_conn


def get_arcsde_connection_object(params: dc.ArcSdeConnParams):

    try:

        if params.conn_file:
            # Caller is supplying a .sde file path
            sde_conn = arcpy.ArcSDESQLExecute(server=params.conn_file)
        elif params.instance and params.database and params.login and params.password:
            sde_conn = arcpy.ArcSDESQLExecute(server=params.instance,
                                              instance=f'sde:sqlserver:{params.instance}',
                                              database=params.database,
                                              user=params.login,
                                              password=params.password)
        else:
            raise Exception('Required parameters not provided') from None

        return sde_conn

    except:
        logh.log_exception()
        raise Exception('Error retrieving default schema') from None

