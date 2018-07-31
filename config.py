"""
Author: Ryan Tompkins

Description: Configuration and constants
"""

# Socrata SOQL filtering on the "borough" col is picky about specific casing
borough_map = {'BRONX': 'Bronx',
               'QUEENS': 'Queens',
               'STATEN ISLAND': 'Staten Island',
               'BROOKLYN': 'Brooklyn',
               'MANHATTAN': 'Manhattan'}

# Socrata SOQL filtering on the "borough" col is picky about specific casing
refuse_map = {'REFUSE': 'Refuse',
               'PAPER': 'Paper',
               'MGP': 'MGP'}

# Constants
socrata_domain = 'data.cityofnewyork.us'
socrata_dataset_identifier = '8bkb-pvci'
socrata_token = 'U4C4lMoTZKonmEzkBh4nJTCjr'
january_2015_filter = '2015 / 01'
api_fields = 'month, borough, communitydistrict, refusetonscollected, papertonscollected, mgptonscollected'
garbage_suffix = 'tonscollected'