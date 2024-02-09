import geopandas as gpd

import numpy as np

inventory_data_extracted=gpd.read_file(r"C:/Users/s-mal/Desktop/Python Software/NavigateLA/hillside_inventory_LA_FINAL/hillside_inventory_LA.geojson")

centerline=gpd.read_file(r"C:/Users/s-mal/Desktop/prepare_final_dataset/Streets_(Centerline).geojson")

inventory_data_extracted["Street_Designation"]=None


for i in range(len(inventory_data_extracted)):
    print(i)
    ids=np.where(np.array(centerline["SECT_ID"],dtype=str)==str(inventory_data_extracted["SECT_ID"][i]))[0]
    if len(ids)!=0:
        j=ids[0]
        inventory_data_extracted["Street_Designation"][i]=centerline["Street_Designation"][j]
   
inventory_data_extracted_designated=inventory_data_extracted.copy()