
# Compare the eelgrass dataset I used for the shoreline modification to the most up to date DFO
# dataset, as well as the most up to date ShoreZone dataset.
# The shoreline mod seagrass dataset had the polys adjusted to the coastline, but I will be
# comparing against the original seagrass polys.

# DFO dataset:
# Ashley can't share her version yet. I will just use the version I got for the Estuaries project.
# This should be current enough. We mainly was to document where the Hakai dataset overpredicted.

import arcpy
import os

gdb = r'C:\Users\cristianij\Documents\Projects\shorelinemod_report\shorelinemod_analysis\shorelinemod_analysis.gdb'
sg_phd = 'seagrass_all_19FINAL'   # copied from chapter 1
sg_dfo = 'eelgrass_BC_polygons_explode'
sg_phd_coastmatch = 'sg_101_retrace'
arcpy.env.workspace = gdb

##########################################################
# PhD polys
# create minimum bounding geometry for clipping
arcpy.MinimumBoundingGeometry_management(sg_phd, 'sg_phd_mbg', 'CONVEX_HULL', 'ALL')
arcpy.CopyFeatures_management('sg_phd_mbg', 'sg_phd_mbg_noUS')
# MANUALLY edit in ArcPro to exclude US meadows
# Clip
arcpy.PairwiseClip_analysis(sg_phd, 'sg_phd_mbg_noUS', 'sg_phd_01_clip')

# DFO polys
# polygons have significant errors in them
# repair takes a while
arcpy.CopyFeatures_management(sg_dfo, 'sgpolys_01_repairgeo')
arcpy.RepairGeometry_management('sgpolys_01_repairgeo')
#arcpy.CheckGeometry_management('sgpolys_01_repairgeo')
# Clip to mbg
arcpy.PairwiseClip_analysis('sgpolys_01_repairgeo', 'sg_phd_mbg_noUS', 'sgpolys_02_clip')

# Based on visual overlap, the DFO dataset has more precise and detailed polys (e.g. multiple small
# polys that are represented as one large general poly in the phd dataset).
# I'm not concerned with these kind of differences since the general length of the coastline with
# seagrass would be roughly the same.
# I'm more interested in where there is no overlap.

# Select from phd where intersecting with dfo, invert selection, copy features.
arcpy.MakeFeatureLayer_management('sg_phd_01_clip', 'temp_phd')
arcpy.SelectLayerByLocation_management('temp_phd', 'INTERSECT', 'sgpolys_02_clip', search_distance=200, invert_spatial_relationship='INVERT')
arcpy.CopyFeatures_management('temp_phd', 'sg_phd_02_noIntersect')
arcpy.Delete_management('temp_phd')

# Select from dfo where intersecting with phd, invert selection, copy features.
arcpy.MakeFeatureLayer_management('sgpolys_02_clip', 'temp_dfo')
arcpy.SelectLayerByLocation_management('temp_dfo', 'INTERSECT', 'sg_phd_01_clip', search_distance=200, invert_spatial_relationship='INVERT')
arcpy.CopyFeatures_management('temp_dfo', 'sgpolys_03_noIntersect')
arcpy.Delete_management('temp_dfo')

# ASSESSMENT

# Visually look where they don't overlap and come up with statements where these generally are and
# why that might be (e.g., modeled data extending out too far).

# Based on visual overlap, the DFO dataset has more precise and detailed polys (e.g. multiple small
# polys that are represented as one large general poly in the phd dataset).
# I'm not concerned with these kind of differences since the general length of the coastline with
# seagrass would be roughly the same.
# I'm more interested in where there is no overlap.

# PhD data:
# Numerous meadows in Discover Islands, Lasqueti Island, Howe Sound, Gulf Islands
# DFO data:
# Sechelt Inlet, Sunshine Coast - Gibsons, Saanich Inlet



#############################################################
# Compare my data to current Shorezone data
# (Copy over processing steps from Estuary analysis)

# There is new data from CORI (Nov 2022), but we will still need to use the old data as well to 
# get full coverage. We just want to know if there is overlap with our seagrass polys.
# http://www.coastalandoceans.com/FormRepository/main.asp

sz_base = r'C:\Users\cristianij\Documents\Projects\Estuary_threats\spatial\01_original\ecological_data_analysis\shorezone'
shorezone_old_ln = os.path.join(sz_base, 'BC_historical_ShoreZone_Mapping_17aug20.gdb/Unit_lines')
shorezone_old_tb = os.path.join(sz_base, 'BC_historical_ShoreZone_Mapping_17aug20.gdb/BioBand')
shorezone_new_ln = os.path.join(sz_base, 'BC_ShoreZone_Mapping_17nov22.gdb/Unit_lines')
shorezone_new_tb = os.path.join(sz_base, 'BC_ShoreZone_Mapping_17nov22.gdb/BioBand')

arcpy.MakeFeatureLayer_management(shorezone_old_ln, 'temp_szoldln')
arcpy.env.qualifiedFieldNames = False
arcpy.AddJoin_management('temp_szoldln', 'PHY_IDENT', shorezone_old_tb, 'PHY_IDENT')
arcpy.CopyFeatures_management('temp_szoldln', 'temp')
where = """ZOS IN ('P', 'C')""" # patchy or continuous
sel = arcpy.SelectLayerByAttribute_management('temp', where_clause=where)
arcpy.CopyFeatures_management(sel, 'temp_shorezoneold')
arcpy.Delete_management(['temp_szoldln', 'temp'])

arcpy.MakeFeatureLayer_management(shorezone_new_ln, 'temp_sznewln')
arcpy.env.qualifiedFieldNames = False
arcpy.AddJoin_management('temp_sznewln', 'PHY_IDENT', shorezone_new_tb, 'PHY_IDENT')
arcpy.CopyFeatures_management('temp_sznewln', 'temp')
where = """EELG IN ('P', 'C')"""
sel = arcpy.SelectLayerByAttribute_management('temp', where_clause=where)
arcpy.CopyFeatures_management(sel, 'temp_shorezonenew')
arcpy.Delete_management(['temp_sznewln', 'temp'])

# add old/new field for distinguishing later
arcpy.AddField_management('temp_shorezoneold', 'new_old', 'TEXT')
with arcpy.da.UpdateCursor('temp_shorezoneold', ['new_old']) as cursor:
    for row in cursor:
        row[0] = 'OLD'
        cursor.updateRow(row)
arcpy.AddField_management('temp_shorezonenew', 'new_old', 'TEXT')
with arcpy.da.UpdateCursor('temp_shorezonenew', ['new_old']) as cursor:
    for row in cursor:
        row[0] = 'NEW'
        cursor.updateRow(row)

# SHOREZONE notes:
# You can have two identical lines for eelgrass presence that have the same PHY_IDENT, and they only
# differ based on the CROSS_LINK field. This will match the PHY_IDENT except for the last two
# slashes. These refer to subtidal, intertidal and supratidal, and then the number breaks these down
# even further (see page 15 in newer 2017 manual).

arcpy.Merge_management(['temp_shorezoneold', 'temp_shorezonenew'], 'temp_shorezone_merge')
arcpy.Delete_management(['temp_shorezonenew', 'temp_shorezoneold'])
arcpy.PairwiseClip_analysis('temp_shorezone_merge', 'sg_phd_mbg_noUS', 'shorezone')
arcpy.Delete_management('temp_shorezone_merge')

# Using seagrass polygons that are matched to coastline, select meadows within X meters, invert
# selection, copy features.
arcpy.MakeFeatureLayer_management(sg_phd_coastmatch, 'temp_phd')
arcpy.SelectLayerByLocation_management('temp_phd', 'INTERSECT', 'shorezone', search_distance= 100, invert_spatial_relationship='INVERT')
arcpy.CopyFeatures_management('temp_phd', 'sg_phd_coastmatch_noIntersect_shorezone')
arcpy.Delete_management('temp_phd')

# Select from shorezone where intersecting with phd, invert selection, copy features.
arcpy.MakeFeatureLayer_management('shorezone', 'temp_sz')
arcpy.SelectLayerByLocation_management('temp_sz', 'INTERSECT', sg_phd_coastmatch, search_distance=100, invert_spatial_relationship='INVERT')
arcpy.CopyFeatures_management('temp_sz', 'shorezone_noIntersect')
arcpy.Delete_management('temp_sz')



# ASSESSMENT
# Shorezone
# Where we might be missing data compared to what Shorezone dataset has:
# Texada Island, throughout Sunshine Coast, small segments throughout Gulf Islands, Vancouver.
# 
# No point in looking at where we have polys but no shorezone, as we already know there are
# numberous polygon sources independent of shorezone. 
