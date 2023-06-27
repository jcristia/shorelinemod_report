

import arcpy
import os
import pandas as pd

base = r'C:\Users\cristianij\Documents\Projects\shorelinemod_report'
shomod_fc = os.path.join(base, 'mapping\shoreline_modification.gdb\sg_106_AREA_type_pt')

# to pandas df
field_names = [i.name for i in arcpy.ListFields(shomod_fc) if i.type != 'OID'] 
cursor = arcpy.da.SearchCursor(shomod_fc, field_names) 
df = pd.DataFrame(data=[row for row in cursor], columns=field_names)
df = df[['uID', 'desc_1', 'shmod_percent']]

##########################################################

# % of meadows that have 80% or greater total modification
df_agg = df.groupby('uID').agg({'shmod_percent':'sum'})
numrows = len(df_agg)
nrows80 = len(df_agg[df_agg.shmod_percent >=80])
nrows50 = len(df_agg[df_agg.shmod_percent >=50])
perc80 = nrows80/numrows*100    # 1.1%

# % of meadows that have 50% or greater total modification
perc50 = nrows50/numrows*100    # 9.0%

# median modification percentage
df_agg.shmod_percent.median()   # 9.1%

# % of meadows with no modifications
nrows0 = len(df_agg[df_agg.shmod_percent==0])
perc0 = nrows0/numrows*100    # 19%

# % with less than 10% modified
nrows10 = len(df_agg[df_agg.shmod_percent<=10])
perc10 = nrows10/numrows*100    # 52%

# number of sites with industrial development above 75%
df_ind = df[df.desc_1 == 'industrial']
df_agg_ind = df_ind.groupby('uID').agg({'shmod_percent':'sum'})
numrows_ind = len(df_agg_ind)
nrows80ind = len(df_agg_ind[df_agg_ind.shmod_percent >=75])   #2
