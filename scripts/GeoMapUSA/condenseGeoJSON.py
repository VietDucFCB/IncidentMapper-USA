#!/usr/bin/env python3

from urllib.request import urlopen
import json
import os
import sys


def generate_usa_geojson():
    """Generate a single GeoJSON file for all US states"""
    print("Generating USA GeoJSON file...")

    # GitHub repository with GeoJSON data
    geoJsonRoot = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/"

    # List of all state GeoJSON files
    geoJsonFiles = [
        'ak_alaska_zip_codes_geo.min.json',
        'al_alabama_zip_codes_geo.min.json',
        'ar_arkansas_zip_codes_geo.min.json',
        'az_arizona_zip_codes_geo.min.json',
        'ca_california_zip_codes_geo.min.json',
        'co_colorado_zip_codes_geo.min.json',
        'ct_connecticut_zip_codes_geo.min.json',
        'dc_district_of_columbia_zip_codes_geo.min.json',
        'de_delaware_zip_codes_geo.min.json',
        'fl_florida_zip_codes_geo.min.json',
        'ga_georgia_zip_codes_geo.min.json',
        'hi_hawaii_zip_codes_geo.min.json',
        'ia_iowa_zip_codes_geo.min.json',
        'id_idaho_zip_codes_geo.min.json',
        'il_illinois_zip_codes_geo.min.json',
        'in_indiana_zip_codes_geo.min.json',
        'ks_kansas_zip_codes_geo.min.json',
        'ky_kentucky_zip_codes_geo.min.json',
        'la_louisiana_zip_codes_geo.min.json',
        'ma_massachusetts_zip_codes_geo.min.json',
        'md_maryland_zip_codes_geo.min.json',
        'me_maine_zip_codes_geo.min.json',
        'mi_michigan_zip_codes_geo.min.json',
        'mn_minnesota_zip_codes_geo.min.json',
        'mo_missouri_zip_codes_geo.min.json',
        'ms_mississippi_zip_codes_geo.min.json',
        'mt_montana_zip_codes_geo.min.json',
        'nc_north_carolina_zip_codes_geo.min.json',
        'nd_north_dakota_zip_codes_geo.min.json',
        'ne_nebraska_zip_codes_geo.min.json',
        'nh_new_hampshire_zip_codes_geo.min.json',
        'nj_new_jersey_zip_codes_geo.min.json',
        'nm_new_mexico_zip_codes_geo.min.json',
        'nv_nevada_zip_codes_geo.min.json',
        'ny_new_york_zip_codes_geo.min.json',
        'oh_ohio_zip_codes_geo.min.json',
        'ok_oklahoma_zip_codes_geo.min.json',
        'or_oregon_zip_codes_geo.min.json',
        'pa_pennsylvania_zip_codes_geo.min.json',
        'ri_rhode_island_zip_codes_geo.min.json',
        'sc_south_carolina_zip_codes_geo.min.json',
        'sd_south_dakota_zip_codes_geo.min.json',
        'tn_tennessee_zip_codes_geo.min.json',
        'tx_texas_zip_codes_geo.min.json',
        'ut_utah_zip_codes_geo.min.json',
        'va_virginia_zip_codes_geo.min.json',
        'vt_vermont_zip_codes_geo.min.json',
        'wa_washington_zip_codes_geo.min.json',
        'wi_wisconsin_zip_codes_geo.min.json',
        'wv_west_virginia_zip_codes_geo.min.json',
        'wy_wyoming_zip_codes_geo.min.json'
    ]

    output_dir = "geojson_output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "USA-all-states.geojson")

    try:
        # Process all GeoJSON files
        features = []
        total_files = len(geoJsonFiles)

        print(f"Downloading {total_files} state files...")

        for i, gj in enumerate(geoJsonFiles):
            try:
                # Download and parse GeoJSON
                file_url = geoJsonRoot + gj
                with urlopen(file_url) as resp:
                    _fc = json.load(resp)

                # Add features to USA collection
                features.extend(_fc['features'])
                sys.stdout.write(f"\rProcessed: {i + 1}/{total_files} files")
                sys.stdout.flush()

            except Exception:
                continue

        print(f"\nCombining {len(features)} features into a single GeoJSON file...")

        # Save USA GeoJSON with .geojson extension
        usa_geojson = {'type': 'FeatureCollection', 'features': features}
        with open(output_file, 'w') as jf:
            json.dump(usa_geojson, jf)

        print(f"Created USA GeoJSON file: {output_file}")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == '__main__':
    print("\nUSA GeoJSON Generator")
    print("Current Date and Time (UTC): 2025-04-14 08:19:02")
    print("User: VietDucFCB\n")

    success = generate_usa_geojson()

    if success:
        print("\nProcess completed successfully!")
    else:
        print("\nProcess completed with errors.")