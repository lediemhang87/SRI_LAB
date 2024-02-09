from selenium import webdriver
import os
import geopandas as gpd
import pandas as pd
import json


# File that you want to change in the local repo
file_path_local = 'hillside_inventory_LA_centrality_full_new_evacmidnorth_UPDATED_copy.geojson'

# Name of the file that are downloaded
file_path_online_width_length_surface = 'StreetsLA_GeoHub_Street_Inventory.geojson'
file_path_online_designation = 'Street Centerline.geojson'

def download_StreetsLA():
    chrome_options = webdriver.ChromeOptions()

    # Set default download directory to be the current working directory
    prefs = {"download.default_directory" : os.getcwd()}
    chrome_options.add_experimental_option("prefs", prefs)
    # Set this so it will not stop downloading in the middle of running
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)

    file_path_width_length_surface = 'StreetsLA_GeoHub_Street_Inventory.geojson' 

    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path_width_length_surface):
        os.remove(file_path_width_length_surface)
        print(f"File '{file_path_width_length_surface}' deleted successfully.")
    else:
        print(f"File '{file_path_width_length_surface}' does not exist.")

    # Download the data
    driver.get('https://opendata.arcgis.com/api/v3/datasets/aaaa5c1b83db4097985a15aba93082d5_0/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1')

    # wait until done downloading
    while not os.path.exists(file_path_width_length_surface):
        pass

    driver.quit()

def download_Centerline():
    chrome_options = webdriver.ChromeOptions()

    # Set default download directory to be the current working directory
    prefs = {"download.default_directory" : os.getcwd()}
    chrome_options.add_experimental_option("prefs", prefs)

    # Set this so it will not stop downloading in the middle of running
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)

    file_path_designation = 'Street Centerline.geojson' 

    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path_designation):
        os.remove(file_path_designation)
        print(f"File '{file_path_designation}' deleted successfully.")
    else:
        print(f"File '{file_path_designation}' does not exist.")

    # Download the data
    driver.get('https://data.lacity.org/api/geospatial/keky-nxxr?method=export&format=GeoJSON')

    # wait until done downloading
    while not os.path.exists(file_path_designation):
        pass

    driver.quit()

def update_st_length_local(file_path_local, file_path_online):
    download_StreetsLA()
    try:
        # Read local GeoJSON file
        gdf_local = gpd.read_file(file_path_local)
        # Read file downloaded from online
        gdf_online = gpd.read_file(file_path_online)

        # Update length, width, surface
        gdf_local['ST_LENGTH'] = gdf_local['SECT_ID'].map(gdf_online.set_index('SECT_ID')['ST_LENGTH'])
        gdf_local['ST_WIDTH'] = gdf_local['SECT_ID'].map(gdf_online.set_index('SECT_ID')['ST_WIDTH'])
        gdf_local['ST_SURFACE'] = gdf_local['SECT_ID'].map(gdf_online.set_index('SECT_ID')['ST_SURFACE'])
        
        # Save the updated GeoDataFrame back to the file
        gdf_local.to_file(file_path_local, driver='GeoJSON')

    except FileNotFoundError:
        print(f"File not found")
    except json.JSONDecodeError as e:
        print(f"Error decoding online JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        os.remove(file_path_online)

def update_designation(file_path_local, file_path_online):
    download_Centerline();
    try:
        gdf_online = gpd.read_file(file_path_online)
        gdf_local = gpd.read_file(file_path_local)

        # Extract the relevant columns from both GeoDataFrames
        online_columns = ['sect_id', 'street_des']
        local_columns = ['SECT_ID', 'Street_Designation']

        # Merge the DataFrames based on the common column 'sect_id' and 'SECT_ID'
        merged_df = pd.merge(gdf_local[local_columns], gdf_online[online_columns], left_on='SECT_ID', right_on='sect_id', how='left')

        # Update the 'Street_Designation' column in the local GeoDataFrame with the values from the online GeoDataFrame
        gdf_local['Street_Designation'] = merged_df['street_des']

        # Print and update local GeoDataFrame
        gdf_local.to_file(file_path_local, driver='GeoJSON')

    except FileNotFoundError:
        print(f"File not found")
    except json.JSONDecodeError as e:
        print(f"Error decoding online JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        os.remove(file_path_online)

if __name__ == "__main__":
    update_st_length_local(file_path_local, file_path_online_width_length_surface)
    update_designation(file_path_local, file_path_online_designation)
    # download_StreetsLA()
    # download_Centerline()
