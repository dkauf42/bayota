import os
import math
import numpy as np
import pandas as pd
import seaborn as sns
from itertools import product

import re

import matplotlib.pyplot as plt
import matplotlib.cm

import geopandas as gpd
from bokeh.models import HoverTool, LogColorMapper, ColorBar, LogTicker, GeoJSONDataSource, LinearColorMapper, ColumnDataSource

lrsegshapefiledir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/data/shapefiles/P6Beta_v3_LRSegs_081516_Albers'

# default namelist file = 'calvertMD_solutionlist_20181210.txt'


def investigate_county(county_name='', state_abbrev='', namelistfile=''):
    """

    Args:
        county_name:
        state_abbrev:

    Returns:

    """
    lrsegs_geometries_df, county_lrsegs_geometries_df, whole_county_geometry_df, county_bounds = load_shapefiles(county_name=county_name,
                                                                                                                 state_abbrev=state_abbrev)

    df, df_single_row_for_each_solution = load_solution_data(namelistfile=namelistfile)

    # Merge Geodata with Solution data
    merged = county_lrsegs_geometries_df.set_index('LndRvrSeg').join(df.set_index('landriversegment'))

    bmptotals_pivoted, merged_costmin_bmptotals, merged_costmin, merged_loadredmax = sum_acres_for_bmps(merged=merged)

    """
    fig, ax = plt.subplots(1, figsize=(12, 8))
    bmptotals_pivoted.plot(ax=ax, marker='.')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    """

    """
    coords = {b: hv.Scatter(merged_costmin_bmptotals.loc[merged_costmin_bmptotals['bmpshortname']==b, :],
                        'percent_reduction_minimum', 'acres')
          for b in list(merged_costmin_bmptotals['bmpshortname'])}

    hv.HoloMap(coords, kdims='BMP')
    """

    constraint_level_selection = 30
    bmpselection = 'ConPlan'
    thismapdf = county_bmp_gdf(constraint_level_selection, bmpselection,
                               merged_costmin, county_lrsegs_geometries_df).loc[:, ['LndRvrSeg',
                                                                                    'acres',
                                                                                    'geometry']]

    thismapdf, geo_source_json, gsource = mapping(thismapdf)

    return df, df_single_row_for_each_solution,\
           bmptotals_pivoted, merged_costmin_bmptotals,\
           merged_costmin, merged_loadredmax,\
           thismapdf, geo_source_json, gsource


def load_shapefiles(county_name='', state_abbrev=''):
    """

    Args:
        county_name:
        state_abbrev:

    Returns:

    """
    # Get shape geometries of all the LRsegs
    fp = os.path.join(lrsegshapefiledir, 'P6Beta_v3_LRSegs_081516_Albers.shp')

    lrsegs_geometries_df = gpd.read_file(fp)

    ''' ---------------- '''
    # Create county-level geodataframe
    # Dissolve LRsegs into county-level geometries
    counties_geometries_df = lrsegs_geometries_df.loc[:, ['ST', 'CNTYNAME', 'geometry']].dissolve(
        by=['ST', 'CNTYNAME']).reset_index()

    # Change the projection of the GeoDataframe to represent the lat/lon
    lrsegs_geometries_df = lrsegs_geometries_df.to_crs({'init': 'epsg:4326'})
    counties_geometries_df = counties_geometries_df.to_crs({'init': 'epsg:4326'})

    ''' ---------------- '''
    # Extract this particular county's geometry
    mask = (counties_geometries_df['CNTYNAME'].str.lower() == county_name.lower()) & (
                counties_geometries_df['ST'].str.lower() == state_abbrev.lower())
    whole_county_geometry_df = counties_geometries_df.loc[mask, :]

    county_bounds = whole_county_geometry_df['geometry'].bounds.reset_index().loc[
        0, ['minx', 'miny', 'maxx', 'maxy']].to_dict()

    ''' ---------------- '''
    # Extract subset of lrsegs located within the county
    mask = (lrsegs_geometries_df['CNTYNAME'].str.lower() == county_name.lower()) & (
                lrsegs_geometries_df['ST'].str.lower() == state_abbrev.lower())
    county_lrsegs_geometries_df = lrsegs_geometries_df.loc[mask, :]

    return lrsegs_geometries_df, county_lrsegs_geometries_df, whole_county_geometry_df, county_bounds


def load_solution_data(namelistfile=''):
    """

    Args:

    Returns:

    """
    output_dir = os.path.dirname(namelistfile)

    with open(namelistfile) as f:
        content = f.readlines()
    filelist = [os.path.join(output_dir, x.strip()) for x in content]

    ''' ---------------- '''
    # Add a column with file names
    dlist = []
    for f in filelist:
        tmpdf = pd.read_csv(f)
        tmpdf['solutionname'] = os.path.basename(f)

        #     (pd.DataFrame.assign)(df, solutionname=os.path.basename(filename))

        dlist.append(tmpdf)
    df = pd.concat(dlist, ignore_index=True, sort=True)

    df = df.loc[df['acres'] >= 0.5, :]

    # Add a column with unique variable (x) names
    df['x'] = list(zip(df.bmpshortname,
                       df.landriversegment,
                       df.loadsource,
                       df.totalannualizedcostperunit))

    df = df.reset_index()

    ''' ---------------- '''
    df['objective_cost'] = df['solution_objective']
    df['objective_loadreduction'] = df['solution_objective']

    df.loc[np.isnan(df.totalcostupperbound), 'objective_loadreduction'] = np.nan
    df.loc[np.isnan(df.percent_reduction_minimum), 'objective_cost'] = np.nan

    ''' ---------------- '''
    # Keep one row for each optimization trial, since we're just looking at objective and constraint values (rather than variable values)
    df_single_row_for_each_solution = df.drop_duplicates(subset=['solutionname'])

    return df, df_single_row_for_each_solution


def sum_acres_for_bmps(merged=None):
    merged_loadredmax = merged.loc[np.isnan(merged['percent_reduction_minimum']), :]
    merged_costmin = merged.loc[np.isnan(merged['totalcostupperbound']), :]

    ''' ---------------- '''
    grouped = merged_costmin.groupby(['percent_reduction_minimum', 'bmpshortname'])
    merged_costmin_bmptotals = grouped[['acres']].sum()

    merged_costmin_bmptotals.reset_index(level=['percent_reduction_minimum', 'bmpshortname'], inplace=True)
    merged_costmin_bmptotals.sort_values(by='percent_reduction_minimum')

    bmptotals_pivoted = merged_costmin_bmptotals.pivot(index='percent_reduction_minimum', columns='bmpshortname',
                                                       values='acres')

    return bmptotals_pivoted, merged_costmin_bmptotals, merged_costmin, merged_loadredmax


def county_bmp_gdf(this_constraint_value, this_bmpshortname, merged_costmin, county_lrsegs_geometries_df):
    # Get data for a single constraint level
    single_constraint_level_data = merged_costmin.loc[
                                   merged_costmin['percent_reduction_minimum'] == this_constraint_value, :]
    # Get data for a single BMP
    thismapdata = single_constraint_level_data.loc[single_constraint_level_data['bmpshortname'] == this_bmpshortname, :]

    grouped = thismapdata.groupby([thismapdata.index.get_level_values(0)])
    mapdata_sum = grouped[['acres']].sum()

    mapdata_merged = county_lrsegs_geometries_df.set_index('LndRvrSeg').join(mapdata_sum)

    mapdata_merged.reset_index(level='LndRvrSeg', inplace=True)

    return mapdata_merged


def mapping(thismapdf):
    thismapdf.dropna(axis='index', how='any', inplace=True)

    # npv = np.array(thismapdf['acres'])
    thismapdf['centerx'] = thismapdf.apply(lambda x: x['geometry'].centroid.x, axis=1)
    thismapdf['centery'] = thismapdf.apply(lambda x: x['geometry'].centroid.y, axis=1)

    # Expand arrays so that point density is equal to 'acres' value
    # thismapdf_expanded = pd.DataFrame(np.repeat(thismapdf.values,
    #                                             np.array(thismapdf['acres']).astype(int),
    #                                             axis=0))
    # thismapdf_expanded.columns = thismapdf.columns
    # np.repeat changed types to string, so change them back to numeric
    # thismapdf_expanded[['acres', 'centerx', 'centery']] = thismapdf_expanded[['acres', 'centerx', 'centery']].apply(
    #     pd.to_numeric)

    # npx_expanded = np.repeat(np.array(thismapdf['centerx']), npv.astype(int))
    # npy_expanded = np.repeat(np.array(thismapdf['centery']), npv.astype(int))

    geo_source_json = GeoJSONDataSource(geojson=thismapdf.to_json())

    gsource = ColumnDataSource(dict(x=np.array(thismapdf['centerx']),
                                    y=np.array(thismapdf['centery']),
                                    acres=np.array(thismapdf['acres']),
                                    LndRvrSeg=thismapdf['LndRvrSeg']))

    return thismapdf, geo_source_json, gsource