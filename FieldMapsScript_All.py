import arcpy

# Run this script externally via propy.bat see "Field Maps Script" in Sci Stew OneNote for more details

# ============================================================
# GLOBAL SETTINGS (shared across all subregions)
# ============================================================

# Path to the ArcGIS Pro project file containing all subregion maps.
APRX_PATH = r"R:\REG_ON\NEW_R_Drive_IN_PROGRESS\SENSITIVE\Field_Maps_Projects\FieldMaps_Script\FieldMaps_Script.aprx"

# Path to the Enterprise GDB .sde connection file.
SDE_CONNECTION = r"R:\REG_ON\NEW_R_Drive_IN_PROGRESS\SENSITIVE\on_data @ NCCSQL02.sde"

# Ontario UTM zones (NAD83) — used to project coordinates zone-by-zone
ACCEPTED_ZONES = (15, 16, 17, 18)

# Set to False to only fill NULL values (safe/incremental mode).
# Set to True to recompute all values regardless of existing data.
OVERWRITE_ATTRS = False

# Standard area field names used across most polygon layers
FIELD_AREA_HA  = "UTM_Ha"   # geodesic hectares
FIELD_AREA_AC  = "UTM_Ac"   # international acres (converted from Ha)
INTERNATIONAL_ACRES_PER_HA = 2.471053814671653

# Standard coordinate/measurement field names 
FIELD_UTM_ZONE = "UTM_Zone"
FIELD_EASTING  = "Easting"
FIELD_NORTHING = "Northing"
FIELD_LEN_UTM  = "Length_UTM"


# ===========================================================================================================================
# SUBREGION CONFIGURATIONS
#
# Each entry in SUBREGIONS defines one map tab in the APRX and
# all the layer names, exceptions, and special cases for that
# subregion.
#
# Keys per entry:
#   map_name - map tab name in the APRX
#   point_layers - list of point layer names
#   line_layers - list of line layer names
#   poly_layers - list of polygon layer names
#   exception_poly_area - layers using non-standard area field names(e.g. Treatment_Area_Ha instead of UTM_Ha in stew action)
#   only_area_poly_layers - layers that have NO UTM_Zone field and should only receive area calculations
# ===========================================================================================================================

SUBREGIONS = [

    # ------------------------------------------------------------------
    # MWO
    # ------------------------------------------------------------------
    {
        "map_name": "MWO",
        "point_layers": [
            "MWO_SARPoint",
            "MWO_InvasivePoint",
            "MWO_AnthroPoint",
            "MWO_EasementPoint",
            "MWO_OtherFeaturePoint",
            "MWO_IssuesPoint",
            "MWO_HazardsPoint",
        ],
        "line_layers": [
            "MWO_SARLine",
            "MWO_InvasiveLine",
            "MWO_AnthroLine",
            "MWO_Trail",
            "MWO_OtherFeatureLine",
            "MWO_EasementLine",
        ],
        "poly_layers": [
            "MWO_SARPoly",
            "MWO_InvasivePoly",
            "MWO_OtherFeaturePoly",
            "MWO_AnthroPoly",
            "MWO_TargetsThreats",
            "MWO_VegetationCommunities",
            "MWO_StewardshipAction",        # exception #1: uses Treatment_Area_* fields
            "MWO_VegCommunityCollection",   # exception #2: areas only, no UTM_Zone
        ],
        "exception_poly_area": {
            "MWO_StewardshipAction": {
                "ha_field": "Treatment_Area_Ha",
                "ac_field": "Treatment_Area_Ac",
                "requires_zone": True,
                "skip_en": False,
                "skip_zone_normalize": False,
                "skip_zone_populate": False,
            }
        },
        "only_area_poly_layers": {"MWO_VegCommunityCollection"},
    },

    # ------------------------------------------------------------------
    # EO
    # ------------------------------------------------------------------
    {
        "map_name": "EO",
        "point_layers": [
            "EO_SARPoint",
            "EO_InvasivePoint",
            "EO_AnthroPoint",
            "EO_Easement_Point",
            "EO_Other_FeaturePoint",
            "EO_Issues_Point",
            "EO_Hazards_Point",
        ],
        "line_layers": [
            "EO_SARLine",
            "EO_InvasiveLine",
            "EO_AnthroLine",
            "EO_Trail",
            "EO_Other_FeatureLine",
            "EO_Easement_Line",
        ],
        "poly_layers": [
            "EO_SARPoly",
            "EO_InvasivePoly",
            "EO_Other_FeaturePoly",
            "EO_AnthroPoly",
            "EO_TargetsThreats",
            "EO_VegetationCommunities",
            "EO_StewardshipAction",         # exception #1: uses Treatment_Area_* fields
            "EO_Veg_CommunityCollection",   # exception #2: areas only, no UTM_Zone
        ],
        "exception_poly_area": {
            "EO_StewardshipAction": {
                "ha_field": "Treatment_Area_Ha",
                "ac_field": "Treatment_Area_Ac",
                "requires_zone": True,
                "skip_en": False,
                "skip_zone_normalize": False,
                "skip_zone_populate": False,
            }
        },
        "only_area_poly_layers": {"EO_Veg_CommunityCollection"},
    },

    # ------------------------------------------------------------------
    # COC
    # ------------------------------------------------------------------
    {
        "map_name": "COC",
        "point_layers": [
            "COC_SAR_Point",
            "COC_Invasive_Point",
            "COC_Anthro_Point",
            "COC_Easement_Point",
            "COC_Other_Feature_Point",
            "COC_Issues_Point",
            "COC_Hazards_Point",
        ],
        "line_layers": [
            "COC_SAR_Line",
            "COC_Invasive_Line",
            "COC_Anthro_Line",
            "COC_Trails",
            "COC_Other_Feature_Line",
            "COC_Easement_Line",
        ],
        "poly_layers": [
            "COC_SAR_Poly",
            "COC_Invasive_Poly",
            "COC_Other_Feature_Poly",
            "COC_Anthro_Poly",
            "COC_Targets_Threats",
            "COC_Vegetation_Communities",
            "COC_Stewardship_Action",         # exception #1: uses Treatment_Area_* fields
            "COC_Veg_Community_Collection",   # exception #2: areas only, no UTM_Zone
        ],
        "exception_poly_area": {
            "COC_Stewardship_Action": {
                "ha_field": "Treatment_Area_Ha",
                "ac_field": "Treatment_Area_Ac",
                "requires_zone": True,
                "skip_en": False,
                "skip_zone_normalize": False,
                "skip_zone_populate": False,
            }
        },
        "only_area_poly_layers": {"COC_Veg_Community_Collection"},
    },

    # ------------------------------------------------------------------
    # COE
    # ------------------------------------------------------------------
    {
        "map_name": "COE",
        "point_layers": [
            "COE_SARPoint",
            "COE_InvasivePoint",
            "COE_AnthroPoint",
            "COE_Easement_Point",
            "COE_Other_FeaturePoint",
            "COE_Issues_Point",
            "COE_Hazards_Point",
        ],
        "line_layers": [
            "COE_SARLine",
            "COE_InvasiveLine",
            "COE_AnthroLine",
            "COE_Trail",
            "COE_Other_FeatureLine",
            "COE_Easement_Line",
        ],
        "poly_layers": [
            "COE_SARPoly",
            "COE_InvasivePoly",
            "COE_Other_FeaturePoly",
            "COE_AnthroPoly",
            "COE_TargetsThreats",
            "COE_VegetationCommunities",
            "COE_StewardshipAction",         # exception #1: uses Treatment_Area_* fields
            "COE_Veg_CommunityCollection",   # exception #2: areas only, no UTM_Zone
        ],
        "exception_poly_area": {
            "COE_StewardshipAction": {
                "ha_field": "Treatment_Area_Ha",
                "ac_field": "Treatment_Area_Ac",
                "requires_zone": True,
                "skip_en": False,
                "skip_zone_normalize": False,
                "skip_zone_populate": False,
            }
        },
        "only_area_poly_layers": {"COE_Veg_CommunityCollection"},
    },
    
    # ------------------------------------------------------------------
    # COW
    # ------------------------------------------------------------------
    {
        "map_name": "COW",
        "point_layers": [
            "COW_SARPoint",
            "COW_InvasivePoint",
            "COW_AnthroPoint",
            "COW_Easement_Point",
            "COW_Other_FeaturePoint",
            "COW_Issues_Point",
            "COW_Hazards_Point",
        ],
        "line_layers": [
            "COW_SARLine",
            "COW_InvasiveLine",
            "COW_AnthroLine",
            "COW_Trail",
            "COW_Other_FeatureLine",
            "COW_Easement_Line",
        ],
        "poly_layers": [
            "COW_SARPoly",
            "COW_InvasivePoly",
            "COW_Other_FeaturePoly",
            "COW_AnthroPoly",
            "COW_TargetsThreats",
            "COW_VegetationCommunities",
            "COW_StewardshipAction",         # exception #1: uses Treatment_Area_* fields
            "COW_Veg_CommunityCollection",   # exception #2: areas only, no UTM_Zone
        ],
        "exception_poly_area": {
            "COW_StewardshipAction": {
                "ha_field": "Treatment_Area_Ha",
                "ac_field": "Treatment_Area_Ac",
                "requires_zone": True,
                "skip_en": False,
                "skip_zone_normalize": False,
                "skip_zone_populate": False,
            }
        },
        "only_area_poly_layers": {"COW_Veg_CommunityCollection"},
    },


    # ------------------------------------------------------------------
    # NO
    # ------------------------------------------------------------------
    {
        "map_name": "NO",
        "point_layers": [
            "NO_SAR_Point",
            "NO_Invasive_Point",
            "NO_Anthro_Point",
            "NO_Easement_Point",
            "NO_Other_Feature_Point",
            "NO_Issues_Point",
            "NO_Hazards_Point",
        ],
        "line_layers": [
            "NO_SAR_Line",
            "NO_Invasive_Line",
            "NO_Anthro_Line",
            "NO_Trails",
            "NO_Other_Feature_Line",
            "NO_Easement_Line",
        ],
        "poly_layers": [
            "NO_SAR_Poly",
            "NO_Invasive_Poly",
            "NO_Other_Feature_Poly",
            "NO_Anthro_Poly",
            "NO_Targets_Threats",
            "NO_Vegetation_Communities",
            "NO_Stewardship_Action",         # exception #1: uses Treatment_Area_* fields
            "NO_Veg_Community_Collection",   # exception #2: areas only, no UTM_Zone
        ],
        "exception_poly_area": {
            "NO_Stewardship_Action": {
                "ha_field": "Treatment_Area_Ha",
                "ac_field": "Treatment_Area_Ac",
                "requires_zone": True,
                "skip_en": False,
                "skip_zone_normalize": False,
                "skip_zone_populate": False,
            }
        },
        "only_area_poly_layers": {"NO_Veg_Community_Collection"},
    },

    # ------------------------------------------------------------------
    # SWO
    # ------------------------------------------------------------------
    {
        "map_name": "SWO",
        "point_layers": [
            "SWO_SARPoint",
            "SWO_InvasivePoint",
            "SWO_AnthroPoint",
            "SWO_Easement_Point",
            "SWO_OtherFeature_Point",
            "SWO_Issues_Point",
            "SWO_Hazards_Point",
        ],
        "line_layers": [
            "SWO_SARLine",
            "SWO_InvasiveLine",
            "SWO_AnthroLine",
            "SWO_Trail",
            "SWO_OtherFeature_Line",
            "SWO_Easement_Line",
        ],
        "poly_layers": [
            "SWO_SARPoly",
            "SWO_InvasivePoly",
            "SWO_OtherFeature_Poly",
            "SWO_AnthroPoly",
            "SWO_TargetsThreats",
            "SWO_VegetationCommunities",
            "SWO_StewardshipAction",         # exception #1: uses Treatment_Area_* fields
            "SWO_Veg_CommunityCollection",   # exception #2: areas only, no UTM_Zone
        ],
        "exception_poly_area": {
            "SWO_StewardshipAction": {
                "ha_field": "Treatment_Area_Ha",
                "ac_field": "Treatment_Area_Ac",
                "requires_zone": True,
                "skip_en": False,
                "skip_zone_normalize": False,
                "skip_zone_populate": False,
            }
        },
        "only_area_poly_layers": {"SWO_Veg_CommunityCollection"},
    },
]

# ============================================================
# UTILITY / HELPER FUNCTIONS
# These handle common tasks reused across multiple steps:
# project access, layer lookup, field validation, scratch
# cleanup, and resolving the correct GP input path for a layer.
# ============================================================


def msg(t):
    print(t)


def get_project():
    """Open and return the ArcGIS Pro project."""
    return arcpy.mp.ArcGISProject(APRX_PATH)


def get_target_map(aprx, map_name):
    """Find and return a map by name from the open project."""
    for m in aprx.listMaps():
        if m.name.lower() == map_name.lower():
            return m
    raise RuntimeError(f"Map '{map_name}' not found. Available: {[m.name for m in aprx.listMaps()]}")


def iter_layers(container):
    """Recursively yield all layers in a map, including those inside group layers."""
    for lyr in container.listLayers():
        yield lyr
        if getattr(lyr, "isGroupLayer", False):
            yield from iter_layers(lyr)


def get_layer(m, name):
    """Find and return a layer by name from a map (case-insensitive)."""
    tgt = name.lower()
    for lyr in iter_layers(m):
        if lyr.name.lower() == tgt:
            return lyr
    raise RuntimeError(f"Layer '{name}' not found in map '{m.name}'. Available: {[l.name for l in iter_layers(m)]}")


def has_fields(layer, needed):
    """Raise an error if any expected fields are missing from the layer schema."""
    fields = {f.name for f in arcpy.ListFields(layer)}
    missing = [f for f in needed if f not in fields]
    if missing:
        raise RuntimeError(f"{layer.name}: Missing required fields {missing}")


def is_zone_text(layer):
    """
    Return True if the UTM_Zone field is stored as text/string.
    This affects how SQL WHERE clauses are constructed for zone filtering
    (quoted string vs unquoted integer).
    Returns False if the field is absent (e.g. areas-only layers).
    """
    try:
        fld = next(f for f in arcpy.ListFields(layer) if f.name == FIELD_UTM_ZONE)
        return fld.type in ("String", "Text")
    except StopIteration:
        return False


def clear_all_selections(m):
    """
    Clear any active selections on all layers in the map before processing.
    Without this, geoprocessing tools would only operate on selected features
    even if the project file was saved with a selection active.
    """
    msg("Clearing all selections in map...")
    for lyr in iter_layers(m):
        try:
            arcpy.management.SelectLayerByAttribute(lyr, "CLEAR_SELECTION")
        except Exception:
            pass
    msg("Selections cleared.")


def get_gp_input(layer):
    """
    Resolve the correct input path for geoprocessing tools.
    For Enterprise GDB (SDE) layers, constructs a direct path using the
    SDE connection file and dataset name to avoid layer object limitations.
    Falls back to the catalog path, then the layer object itself.
    """
    cp = getattr(layer, "connectionProperties", None)
    if isinstance(cp, dict):
        ws_factory = (cp.get("workspace_factory") or "").upper()
        dataset = cp.get("dataset")
        if ws_factory == "SDE" and dataset and SDE_CONNECTION:
            return f"{SDE_CONNECTION}\\{dataset}"
    try:
        desc = arcpy.Describe(layer)
        cat = getattr(desc, "catalogPath", None)
        if cat:
            return cat
    except Exception:
        pass
    return layer


def cleanup_scratch_gdb():
    """
    Delete all temporary feature layers and tables created during processing.
    These are identifiable by their name prefixes. Cleaning up prevents the
    scratch GDB from accumulating stale data across runs.
    """
    scratch = arcpy.env.scratchGDB
    delete_prefixes = (
        "pts_", "ln_", "ply_", "ln_len_", "ply_area_", "ply_area_ha_", "ply_area_ac_",
        "ln_missing_en_", "ln_fix_zone_", "ln_fix_en_", "ln_fix_len_", "utmaz_"
    )
    try:
        arcpy.env.workspace = scratch
        items = (arcpy.ListFeatureClasses() or []) + (arcpy.ListTables() or [])
        for item in items:
            if any(item.startswith(p) for p in delete_prefixes):
                try:
                    arcpy.management.Delete(item)
                    msg(f"    deleted: {item}")
                except Exception as e:
                    msg(f"    could not delete {item} (likely locked): {e}")
    except Exception as e:
        msg(f"  Scratch cleanup failed: {e}")
    finally:
        arcpy.env.workspace = None


def _get_poly_area_fields(layer_name, exception_poly_area):
    """
    Return the (ha_field, ac_field) pair for a polygon layer.
    Most layers use the standard UTM_Ha / UTM_Ac fields.
    Exception layers (e.g. StewardshipAction) use Treatment_Area_Ha / _Ac instead.
    """
    if layer_name in exception_poly_area:
        d = exception_poly_area[layer_name]
        return d["ha_field"], d["ac_field"]
    return FIELD_AREA_HA, FIELD_AREA_AC


# ============================================================
# STEP 1 — POPULATE UTM ZONE
# Calculates which Ontario UTM zone (15–18) each feature falls
# in based on the longitude of its centroid. This value is
# written to the UTM_Zone field and is used in Steps 2–4 to
# apply the correct NAD83 UTM projection zone-by-zone when
# calculating projected coordinates and lengths.
#
# Skipped for areas-only polygon layers (no UTM_Zone field).
# ============================================================

def populate_utm_zone(layer, overwrite, cfg):
    if layer.name in cfg["only_area_poly_layers"]:
        msg(f"[{layer.name}] Skipping UTM_Zone population (areas-only layer).")
        return

    msg(f"[{layer.name}] Step 1: Populating UTM_Zone (overwrite={overwrite})")
    z_text = is_zone_text(layer)
    src = get_gp_input(layer)

    # Skip if the UTM_Zone field doesn't exist on this layer
    if FIELD_UTM_ZONE not in {f.name for f in arcpy.ListFields(src)}:
        msg(f"{FIELD_UTM_ZONE} field not present; skipping.")
        return

    # Target only NULL rows unless overwrite mode is on
    where = "" if overwrite else (
        f"({FIELD_UTM_ZONE} IS NULL OR {FIELD_UTM_ZONE}='')" if z_text
        else f"{FIELD_UTM_ZONE} IS NULL"
    )
    tmp = arcpy.CreateUniqueName(f"utmaz_{layer.name}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(src, tmp, where)
    cnt = int(arcpy.management.GetCount(tmp)[0])
    msg(f"Features to update: {cnt}")
    if cnt == 0:
        return

    # Arcade expression: derive UTM zone from centroid longitude
    # Zone = floor((longitude + 180) / 6) + 1
    if z_text:
        expr = (
            "if ($feature==null) return null;"
            "var g = Geometry($feature);"
            "if (g==null || IsEmpty(g)) return null;"
            "var lon = Centroid(g).x;"
            "var z = Floor((lon+180)/6) + 1;"
            "return Text(z);"
        )
    else:
        expr = (
            "if ($feature==null) return null;"
            "var g = Geometry($feature);"
            "if (g==null || IsEmpty(g)) return null;"
            "var lon = Centroid(g).x;"
            "return Floor((lon+180)/6) + 1;"
        )
    arcpy.management.CalculateField(tmp, FIELD_UTM_ZONE, expr, "ARCADE")
    msg("UTM_Zone populated.")


# ============================================================
# STEP 2 — POINT COORDINATES (Easting / Northing)
# Projects each point into its correct NAD83 UTM zone and
# writes the X/Y coordinates to the Easting and Northing
# fields. Features are processed zone-by-zone so the correct
# UTM projection is applied to each group.
# ============================================================

def calc_point_en(layer, zones, overwrite):
    msg(f"  [{layer.name}] Step 2: Calculating point Easting/Northing (NAD83 UTM)")
    z_text = is_zone_text(layer)
    src = get_gp_input(layer)

    if FIELD_UTM_ZONE not in {f.name for f in arcpy.ListFields(src)}:
        msg(f"{FIELD_UTM_ZONE} field not present; skipping.")
        return

    for z in zones:
        # Filter to features in this zone that need coordinates
        where = f"{FIELD_UTM_ZONE}='{z}'" if z_text else f"{FIELD_UTM_ZONE}={z}"
        if not overwrite:
            where += f" AND ({FIELD_EASTING} IS NULL OR {FIELD_NORTHING} IS NULL)"
        tmp = arcpy.CreateUniqueName(f"pts_{layer.name}_z{z}".replace(" ", "_"), arcpy.env.scratchGDB)
        arcpy.management.MakeFeatureLayer(src, tmp, where)
        cnt = int(arcpy.management.GetCount(tmp)[0])
        msg(f"    Zone {z}: {cnt} point(s) to update")
        if cnt > 0:
            sr = arcpy.SpatialReference(26900 + z)  # e.g. zone 17 = EPSG 26917
            arcpy.management.CalculateGeometryAttributes(
                tmp,
                geometry_property=[[FIELD_EASTING, "POINT_X"], [FIELD_NORTHING, "POINT_Y"]],
                coordinate_system=sr
            )
            msg(f"Zone {z}: updated {cnt} points")


# ============================================================
# STEP 3 — LINE COORDINATES AND LENGTH
# For lines, Easting/Northing are derived from the line's
# centroid, projected zone-by-zone into NAD83 UTM (same
# approach as points). Geodesic length in metres is also
# calculated and written to Length_UTM.
#
# After the main calculation, a QA pass identifies any lines
# still missing EN values (e.g. due to a bad/missing UTM_Zone),
# audits them by reporting their geometry-derived zone vs stored
# zone, then attempts to fix them by recomputing UTM_Zone from
# the centroid before recalculating EN and length.
# ============================================================

def calc_line_en_len(layer, overwrite):
    msg(f"[{layer.name}] Step 3: Calculating line Easting/Northing + geodesic length")
    z_text = is_zone_text(layer)
    src = get_gp_input(layer)

    if FIELD_UTM_ZONE in {f.name for f in arcpy.ListFields(src)}:
        for z in ACCEPTED_ZONES:
            where = f"{FIELD_UTM_ZONE}='{z}'" if z_text else f"{FIELD_UTM_ZONE}={z}"
            if not overwrite:
                where += f" AND ({FIELD_EASTING} IS NULL OR {FIELD_NORTHING} IS NULL)"
            tmp = arcpy.CreateUniqueName(f"ln_{layer.name}_z{z}".replace(" ", "_"), arcpy.env.scratchGDB)
            arcpy.management.MakeFeatureLayer(src, tmp, where)
            cnt = int(arcpy.management.GetCount(tmp)[0])
            msg(f"    Zone {z}: {cnt} line(s) to update EN")
            if cnt > 0:
                sr = arcpy.SpatialReference(26900 + z)
                arcpy.management.CalculateGeometryAttributes(
                    tmp,
                    geometry_property=[[FIELD_EASTING, "CENTROID_X"], [FIELD_NORTHING, "CENTROID_Y"]],
                    coordinate_system=sr
                )
                msg(f"Zone {z}: EN updated")
    else:
        msg(f"{FIELD_UTM_ZONE} field not present; skipping EN calculation.")

    # Geodesic length is calculated globally (not zone-dependent)
    tmp_len = arcpy.CreateUniqueName(f"ln_len_{layer.name}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(src, tmp_len, "" if overwrite else f"{FIELD_LEN_UTM} IS NULL")
    arcpy.management.CalculateGeometryAttributes(
        tmp_len,
        geometry_property=[[FIELD_LEN_UTM, "LENGTH_GEODESIC"]],
        length_unit="METERS"
    )
    msg("Geodesic lengths updated")


def report_lines_missing_en(layer):
    """
    QA check: report how many lines are still missing EN after Step 3,
    and print a sample of their OIDs for investigation.
    """
    tmp = arcpy.CreateUniqueName(f"ln_missing_en_{layer.name}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(
        get_gp_input(layer), tmp,
        f"{FIELD_EASTING} IS NULL OR {FIELD_NORTHING} IS NULL"
    )
    cnt = int(arcpy.management.GetCount(tmp)[0])
    msg(f"  [{layer.name}] Lines still missing EN after Step 3: {cnt}")
    if cnt > 0:
        oids = []
        with arcpy.da.SearchCursor(tmp, ["OID@"]) as cur:
            for i, (oid,) in enumerate(cur):
                oids.append(oid)
                if i >= 19:
                    break
        msg(f"Sample OIDs (first 20): {oids}")


def audit_lines_missing_en(layer):
    """
    QA audit: for each line still missing EN, compare the stored UTM_Zone
    value against the zone derived from actual centroid geometry. This helps
    diagnose whether the issue is a bad stored zone value or an empty geometry.
    """
    msg(f"[{layer.name}] Auditing lines missing EN...")
    src = get_gp_input(layer)
    tmp = arcpy.CreateUniqueName(f"ln_missing_en_{layer.name}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(src, tmp, f"{FIELD_EASTING} IS NULL OR {FIELD_NORTHING} IS NULL")
    cnt = int(arcpy.management.GetCount(tmp)[0])
    msg(f"    Missing EN count: {cnt}")
    if cnt == 0:
        return
    wgs84 = arcpy.SpatialReference(4326)
    with arcpy.da.SearchCursor(tmp, ["OID@", FIELD_UTM_ZONE, "SHAPE@"]) as cur:
        for oid, zval, shp in cur:
            if shp is None or shp.isEmpty:
                msg(f"    OID {oid}: UTM_Zone={zval} | GEOMETRY=EMPTY/NULL -> re-digitize")
                continue
            try:
                c = shp.trueCentroid if shp.trueCentroid else shp.centroid
                c_wgs = arcpy.PointGeometry(c, shp.spatialReference).projectAs(wgs84)
                lon = c_wgs.firstPoint.X
                derived = int((lon + 180.0) // 6.0) + 1
            except Exception:
                lon, derived = None, None
            msg(f"OID {oid}: UTM_Zone={zval} | lon={lon} | derived_zone={derived}")


def fix_line_zones_from_centroid(layer):
    """
    Fix attempt: for lines still missing EN, recompute UTM_Zone from
    centroid geometry and then recalculate EN and length. This catches
    cases where the stored UTM_Zone was wrong or NULL, which caused
    those features to be skipped during the zone-filtered EN calculation.
    """
    msg(f"  [{layer.name}] Attempting to fix UTM_Zone and EN for lines still missing EN...")
    z_text = is_zone_text(layer)
    src = get_gp_input(layer)
    tmp_missing = arcpy.CreateUniqueName(f"ln_fix_zone_{layer.name}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(src, tmp_missing, f"{FIELD_EASTING} IS NULL OR {FIELD_NORTHING} IS NULL")
    cnt = int(arcpy.management.GetCount(tmp_missing)[0])
    msg(f"    Candidates: {cnt}")
    if cnt == 0:
        return

    if FIELD_UTM_ZONE not in {f.name for f in arcpy.ListFields(tmp_missing)}:
        msg(f"    {FIELD_UTM_ZONE} field not present; cannot fix.")
        return

    # Recompute UTM_Zone from centroid longitude
    if z_text:
        expr = (
            "if ($feature==null) return null;"
            "var g=Geometry($feature);"
            "if (g==null||IsEmpty(g)) return null;"
            "var lon=Centroid(g).x;"
            "return Text(Floor((lon+180)/6)+1);"
        )
    else:
        expr = (
            "if ($feature==null) return null;"
            "var g=Geometry($feature);"
            "if (g==null||IsEmpty(g)) return null;"
            "var lon=Centroid(g).x;"
            "return Floor((lon+180)/6)+1;"
        )
    arcpy.management.CalculateField(tmp_missing, FIELD_UTM_ZONE, expr, "ARCADE")
    msg("UTM_Zone recomputed from centroid.")

    # Recalculate EN using the corrected zone values
    for z in ACCEPTED_ZONES:
        where = f"{FIELD_UTM_ZONE}='{z}'" if z_text else f"{FIELD_UTM_ZONE}={z}"
        tmp_zone = arcpy.CreateUniqueName(f"ln_fix_en_{layer.name}_z{z}".replace(" ", "_"), arcpy.env.scratchGDB)
        arcpy.management.MakeFeatureLayer(tmp_missing, tmp_zone, where)
        cnt_z = int(arcpy.management.GetCount(tmp_zone)[0])
        if cnt_z == 0:
            continue
        sr = arcpy.SpatialReference(26900 + z)
        arcpy.management.CalculateGeometryAttributes(
            tmp_zone,
            geometry_property=[[FIELD_EASTING, "CENTROID_X"], [FIELD_NORTHING, "CENTROID_Y"]],
            coordinate_system=sr
        )
        msg(f"EN fixed for {cnt_z} line(s) in zone {z}")

    # Recalculate length for previously-missing lines
    tmp_len = arcpy.CreateUniqueName(f"ln_fix_len_{layer.name}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(tmp_missing, tmp_len, "")
    arcpy.management.CalculateGeometryAttributes(
        tmp_len,
        geometry_property=[[FIELD_LEN_UTM, "LENGTH_GEODESIC"]],
        length_unit="METERS"
    )
    msg("Length recalculated for fixed lines.")


# ============================================================
# STEP 4 — POLYGON COORDINATES AND AREA
# For polygons, Easting/Northing are derived from the polygon
# centroid (same zone-by-zone approach as lines).
#
# Area is calculated geodesically in hectares, then converted
# to international acres using the standard conversion factor.
# Most layers write to UTM_Ha / UTM_Ac. Exception layers
# (StewardshipAction) write to Treatment_Area_Ha / _Ac instead.
#
# Areas-only layers (VegCommunityCollection) skip the EN
# calculation entirely since they have no UTM_Zone field.
# ============================================================

def calc_poly_en_area(layer, overwrite, cfg):
    lname = layer.name
    only_area = cfg["only_area_poly_layers"]
    exception_poly_area = cfg["exception_poly_area"]

    msg(f"[{lname}] Step 4: Calculating polygon Easting/Northing + area (Ha + Acres)")
    z_text = is_zone_text(layer)
    src = get_gp_input(layer)
    ha_field, ac_field = _get_poly_area_fields(lname, exception_poly_area)

    # 4A) Easting/Northing from centroid, per UTM zone
    # Skipped entirely for areas-only layers that have no UTM_Zone field
    if lname not in only_area:
        if FIELD_UTM_ZONE in {f.name for f in arcpy.ListFields(src)}:
            for z in ACCEPTED_ZONES:
                where = f"{FIELD_UTM_ZONE}='{z}'" if z_text else f"{FIELD_UTM_ZONE}={z}"
                if not overwrite:
                    where += f" AND ({FIELD_EASTING} IS NULL OR {FIELD_NORTHING} IS NULL)"
                tmp_en = arcpy.CreateUniqueName(f"ply_{lname}_z{z}".replace(" ", "_"), arcpy.env.scratchGDB)
                arcpy.management.MakeFeatureLayer(src, tmp_en, where)
                cnt_en = int(arcpy.management.GetCount(tmp_en)[0])
                msg(f"Zone {z}: {cnt_en} polygon(s) to update EN")
                if cnt_en > 0:
                    sr = arcpy.SpatialReference(26900 + z)
                    arcpy.management.CalculateGeometryAttributes(
                        tmp_en,
                        geometry_property=[[FIELD_EASTING, "CENTROID_X"], [FIELD_NORTHING, "CENTROID_Y"]],
                        coordinate_system=sr
                    )
                    msg(f"Zone {z}: EN updated")
        else:
            msg(f"{FIELD_UTM_ZONE} field not present; skipping EN for {lname}.")

    # 4B) Geodesic area in hectares
    # Geodesic calculation accounts for the curvature of the earth,
    # giving more accurate results than planar area for large polygons
    tmp_ha = arcpy.CreateUniqueName(f"ply_area_ha_{lname}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(src, tmp_ha, "" if overwrite else f"{ha_field} IS NULL")
    cnt_ha = int(arcpy.management.GetCount(tmp_ha)[0])
    msg(f"    Hectares: {cnt_ha} polygon(s) to update {ha_field}")
    if cnt_ha > 0:
        arcpy.management.CalculateGeometryAttributes(
            tmp_ha,
            geometry_property=[[ha_field, "AREA_GEODESIC"]],
            area_unit="HECTARES"
        )
        msg(f"{ha_field} updated (geodesic hectares)")

    # 4C) International acres derived from hectares
    # Calculated from the Ha field rather than directly from geometry
    # to ensure Ha and Ac values are always consistent with each other
    tmp_ac = arcpy.CreateUniqueName(f"ply_area_ac_{lname}".replace(" ", "_"), arcpy.env.scratchGDB)
    arcpy.management.MakeFeatureLayer(
        src, tmp_ac,
        "" if overwrite else f"{ac_field} IS NULL AND {ha_field} IS NOT NULL"
    )
    cnt_ac = int(arcpy.management.GetCount(tmp_ac)[0])
    msg(f"    Acres: {cnt_ac} polygon(s) to update {ac_field}")
    if cnt_ac > 0:
        arcpy.management.CalculateField(tmp_ac, ac_field, f"!{ha_field}! * {INTERNATIONAL_ACRES_PER_HA}", "PYTHON3")
        msg(f"    {ac_field} updated (international acres)")


# ============================================================
# PER-SUBREGION RUNNER
# Orchestrates all steps for a single subregion map:
#   1. Opens the correct map tab and clears any active selections
#   2. Resolves all layer objects from their names
#   3. Validates that required fields exist in the schema
#   4. Runs Steps 1–4 in sequence across all layer types
# ============================================================

def run_subregion(aprx, cfg):
    map_name = cfg["map_name"]
    msg(f"\n{'=' * 60}")
    msg(f"  SUBREGION: {map_name}")
    msg(f"{'=' * 60}")

    m = get_target_map(aprx, map_name)
    clear_all_selections(m)

    # Resolve layer names to layer objects
    pts   = [get_layer(m, x) for x in cfg["point_layers"]]
    lns   = [get_layer(m, x) for x in cfg["line_layers"]]
    polys = [get_layer(m, x) for x in cfg["poly_layers"]]

    only_area = cfg["only_area_poly_layers"]
    exc       = cfg["exception_poly_area"]

    # Validate schema before doing any writes —
    # fail fast here rather than partway through processing
    msg("  Validating fields...")
    for lyr in pts:
        has_fields(lyr, [FIELD_UTM_ZONE, FIELD_EASTING, FIELD_NORTHING])
    for lyr in lns:
        has_fields(lyr, [FIELD_UTM_ZONE, FIELD_EASTING, FIELD_NORTHING, FIELD_LEN_UTM])
    for lyr in polys:
        if lyr.name not in only_area:
            has_fields(lyr, [FIELD_UTM_ZONE, FIELD_EASTING, FIELD_NORTHING])
        ha_field, ac_field = _get_poly_area_fields(lyr.name, exc)
        has_fields(lyr, [ha_field, ac_field])
    msg("  Field validation OK.")

    # Step 1: Populate UTM_Zone for all layer types
    for lyr in pts + lns + polys:
        populate_utm_zone(lyr, OVERWRITE_ATTRS, cfg)

    # Step 2: Calculate Easting/Northing for point layers
    for lyr in pts:
        calc_point_en(lyr, ACCEPTED_ZONES, OVERWRITE_ATTRS)

    # Step 3: Calculate Easting/Northing + length for line layers,
    # followed by QA reporting and a fix pass for any holdouts
    for lyr in lns:
        calc_line_en_len(lyr, OVERWRITE_ATTRS)
        report_lines_missing_en(lyr)
        audit_lines_missing_en(lyr)
        fix_line_zones_from_centroid(lyr)

    # Step 4: Calculate Easting/Northing + area (Ha + Ac) for polygon layers
    for lyr in polys:
        calc_poly_en_area(lyr, OVERWRITE_ATTRS, cfg)

    msg(f"\n  Subregion {map_name} COMPLETE.")


# ============================================================
# MAIN
# Entry point. Opens the project once and loops through all
# configured subregions in sequence. If a subregion fails
# (e.g. a missing map tab or layer), the error is logged and
# the script continues to the next subregion rather than
# stopping entirely. Scratch GDB is cleaned after each
# subregion regardless of success or failure.
# ============================================================

def main():
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False
    if SDE_CONNECTION:
        arcpy.env.workspace = SDE_CONNECTION

    msg("Opening project...")
    aprx = get_project()

    for cfg in SUBREGIONS:
        try:
            run_subregion(aprx, cfg)
        except Exception as e:
            msg(f"\n  ERROR in subregion '{cfg['map_name']}': {e}")
            msg("  Skipping to next subregion.\n")
        finally:
            msg("Cleaning scratch workspace...")
            cleanup_scratch_gdb()

    msg("\n ALL SUBREGIONS COMPLETE")


if __name__ == "__main__":
    main()
