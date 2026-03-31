# IMPORTS
from datetime import datetime as dt

class ArcSdeConnParams:
    """Parameters used for the creation of an arcpy.ArcSDESQLExecute class instance.

    Inputs:
    - conn_file: Path to an existing esri database connection file.
    - instance: the name of the SQL Server instance
    - database: the name of the database
    - login: the SQL Server login
    - password: the login password

    If **conn_file** is provided, the other inputs are not required.
    If **conn_file** is not provided, all other inputs are required.
    """

    def __init__(
            self,
            conn_file: str = '',
            instance: str = '',
            database: str = '',
            login: str = '',
            password: str = ''
    ) -> None:
        self.conn_file = conn_file
        self.instance = instance
        self.database = database
        self.login = login
        self.password = password


class FeatureClassObj:

    def __init__(
            self,
            name: str,
            shape_type: str,
            has_area_ha: bool = False,
            has_area_ac: bool = False,
            has_length_m: bool = False,
            has_easting: bool = False,
            has_northing: bool = False,
            has_zone: bool = False,
            fld_area_ha: str = '',
            fld_area_ac: str = '',
            fld_length_m: str = '',
            fld_easting: str = '',
            fld_northing: str = '',
            fld_zone: str = ''
    ) -> None:
        self.name = name
        self.shape_type = shape_type
        self.has_area_ha = has_area_ha
        self.has_area_ac = has_area_ac
        self.has_length_m = has_length_m
        self.has_easting = has_easting
        self.has_northing = has_northing
        self.has_zone = has_zone
        self.fld_area_ha = fld_area_ha
        self.fld_area_ac = fld_area_ac
        self.fld_length_m = fld_length_m
        self.fld_easting = fld_easting
        self.fld_northing = fld_northing
        self.fld_zone = fld_zone


class TrackPointClass:
    """This class defines an AGOL Track Point.  It contains class-wide field names and aliases, as well as instance-specific values
    """

    # Objects -> Tuple(name, alias)
    fc_track_point_all = ('agol_track_point_all', 'AGOL Track Points - All')
    fc_track_point_low_accuracy = ('agol_track_point_low_accuracy', 'AGOL Track Points - Low Accuracy')
    fc_track_point_orphan = ('agol_track_point_orphan', 'AGOL Track Points - Orphan')
    fc_track_point_main = ('agol_track_point_main', 'AGOL Track Points - Main')

    # Fields
    fld_created_user = ('created_user', 'Created User')
    fld_user = ('user', 'AGOL User')
    fld_date_group = ('date_group', 'Date Group')
    fld_full_name = ('full_name', 'Full Name')
    fld_group_key = ('group_key', 'Group Key')
    fld_horizontal_accuracy = ('horizontal_accuracy', 'Horizontal Accuracy')
    fld_identifier = ('identifier', 'Identifier')
    fld_location_timestamp = ('location_timestamp', 'Location Timestamp')
    fld_session_id = ('session_id', 'Session ID')
    fld_shape = ('shape', 'Shape')
    fld_shapeXYToken = ('Shape@XY', 'Shape XY')

    def __init__(
        self,
        user: str,
        location_timestamp: dt,
        session_id: str,
        xy_tuple: tuple[float, float]
    ) -> None:
        self.user = user
        self.location_timestamp = location_timestamp
        self.session_id = session_id
        self.xy_tuple = xy_tuple
