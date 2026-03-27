
# IMPORTS!
import arcpy
from enum import Enum

SR_WKT_ALBERS_WGS84 = 'PROJCS["WGS_1984_Canada_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",\
                       SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],\
                       UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],\
                       PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-96.0],\
                       PARAMETER["Standard_Parallel_1",50.0],PARAMETER["Standard_Parallel_2",70.0],\
                       PARAMETER["Latitude_Of_Origin",40.0],UNIT["Meter",1.0]]'


def get_duration_message(seconds):
    """Construct a time duration message"""

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    # Convert to integers (not seconds, though)
    h = int(h)
    m = int(m)

    # Hours part
    if h > 0:
        part_hours = f'{h} hour{"" if h == 1 else "s"}, '
    else:
        part_hours = ''

    # Minutes part
    if h > 0 or m > 0:
        part_minutes = f'{m} minute{"" if m == 1 else "s"}, '
    else:
        part_minutes = ''

    # Seconds part
    if h > 0 or m > 0 or s > 0:
        if s == 1.0:
            part_seconds = '1 second'
        else:
            part_seconds = f'{s:.1f} seconds'
    else:
        part_seconds = 'instantaneous completion.  what?'

    return f'{part_hours}{part_minutes}{part_seconds}'


def get_sr_pcs_albers_wgs84():
    sr = arcpy.SpatialReference()
    sr.loadFromString(SR_WKT_ALBERS_WGS84)
    return sr


def get_sr_gcs_wgs84():
    return arcpy.SpatialReference(4326)


def get_sr_pcs_web_mercator():
    return arcpy.SpatialReference(3857)


def get_sr_pcs_naequi_wgs84():
    return arcpy.SpatialReference(27705)


def get_sr_pcs_canada_lcc_wgs84():
    return arcpy.SpatialReference(102215)


def get_sr_pcs_agri_albers_wgs84():
    return arcpy.SpatialReference(10820)


class EnvVar(Enum):
    # notifications
    ITGEO_SMTP_SERVER='ITGEO_SMTP_SERVER'
    ITGEO_SMTP_PORT='ITGEO_SMTP_PORT'
    ITGEO_SMTP_LOGIN='ITGEO_SMTP_LOGIN'
    ITGEO_SMTP_PASSWORD='ITGEO_SMTP_PASSWORD'
    ITGEO_SMTP_SENDER='ITGEO_SMTP_SENDER'

class ShapeType(Enum):
    POINT='point'
    MULTIPOINT='multipoint'
    POLYLINE='polyline'
    POLYGON='polygon'