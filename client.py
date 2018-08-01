"""
Author: Ryan Tompkins
File: A Socrata API client that reports garbage collection rates in NYC.

Open dataset from: https://dev.socrata.com/foundry/data.cityofnewyork.us/8bkb-pvci

Database framework 'Dataset' see: https://dataset.readthedocs.io/en/latest/index.html
"""

# READ ME
# make sure to install these packages before running:
# pip install pandas
# pip install sodapy
# pip install dataset

# example usage: python3 client.py -b Bronx -t PAPER -d 9
#              : python3 client.py -b BROOKLYN -t mgp -d 01
#              : python3 client.py -get_total

import pandas as pd
from sodapy import Socrata
import argparse
from config import *
import dataset

# connecting to a SQLite database, creates 'mydatabase.db' in cwd if not already created
# "Clear" the database by running: 'rm mydatabase.db && python3 client.py -get_total'
db = dataset.connect('sqlite:///mydatabase.db')

# global client, connect to the endpoint with the given application token
client = Socrata(socrata_domain, socrata_token)

"""
Query the socrata_domain API endpoint and return the amount of refuse collected in a NYC borough during January 2015:

     params: borough - A string representing an NYC borough
             district - A string representing the borough's district number (under 10 is 0 prefixed like "01")
             refuse_type - A string in the set: [refuse, paper, mpg] to specify the type of garbage queried

     return: An integer representing the number of tons of refuse_type garbage collected in the borough's district
"""
def query_api(borough, district):
    results = client.get(socrata_dataset_identifier,
                         select=api_fields,
                         month=january_2015_filter,
                         borough=borough,
                         communitydistrict=district)

    results_df = pd.DataFrame.from_records(results)

    return results_df


"""
Insert a new entry or update a specific entry via dataset

     params: entry - a district record with populated attributes
"""
def upsert(entry):
    table = db['district']
    table.upsert(dict(communitydistrict=entry['communitydistrict'].tolist()[0],
                      borough=entry['borough'].tolist()[0],
                      refusetonscollected=entry['refusetonscollected'].tolist()[0],
                      papertonscollected=entry['papertonscollected'].tolist()[0],
                      mgptonscollected=entry['mgptonscollected'].tolist()[0]), ['communitydistrict'])


"""
Wrapper function to parse command line arguments:

Arguments:
    -t, --type : the type of garbage to be queried (paper, refuse, mgp)
    -b, --borough : one of the five boroughs in New York City
    -d, --district : one of the numbered districts in a borough ranging from [1..18]
    -get_total: (optional) If set, reports the total refuse collected in all queried communities
"""
def parseArgs():
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--type", required=False)
    ap.add_argument("-b", "--borough", required=False)
    ap.add_argument("-d", "--district", required=False)
    ap.add_argument("-get_total", default=False, action='store_true')
    args = vars(ap.parse_args())

    return args


"""
Validate the arguments used for the NYPD Tonnage API Endpoint

     params: borough - A string representing an NYC borough
             refuse_type - A string in the set: [refuse, paper, mpg] to specify the type of garbage queried
             district - A string representing the borough's district number (under 10 is 0 prefixed like "01")

     return: A tuple (error_code, error_messages) reporting any errors and malformed parameters
"""
def validate_args(borough, refuse_type, district):
    error_code = 0
    error_messages = []

    if borough is None or refuse_type is None or district is None:
        error_messages.append("Error: A valid borough, "
                              "refuse_type, and district number must be provided to make an API query.")
        error_code = -1

    # This supports case-insensitive Boroughs that are spelled correctly
    if borough and borough.upper() not in borough_map.keys():
        error_messages.append('Error: Borough not recognized.')
        error_code = -1

    # This supports case-insensitive refuse that are correctly spelled
    if refuse_type and refuse_type.upper() not in refuse_map.keys():
        error_messages.append('Error: Type of garbage not recognized.')
        error_code = -1

    # ensure the user entered an integer for the district number or the SOQL call will fail
    try:
        if district:
            int(district)
    except:
        error_messages.append('Error: district should be a number in the range [01-18]')
        error_code = -1

    if error_code < 0:
        error_messages.append('Exiting with error code 0')
    else:
        print('Argument validation successful... querying API: \n')

    return error_code, error_messages


"""
Parse and validate the given command line arguments used for the NYPD Tonnage API Endpoint

     return: A tuple (borough, refuse_type, district, get_total, error_code, error_messages)
"""
def parse_and_validate_args():
    args = parseArgs()
    borough, district, refuse_type, get_total = args['borough'], args['district'], args['type'], args['get_total']

    error_code, error_messages = validate_args(borough, refuse_type, district)
    if error_code < 0:
        return '', '', '', get_total, error_code, error_messages

    # reformat the arguments to match the expected SOQL format (i.e. capitals for refuse, not for Borough)
    borough = borough_map[borough.upper()]
    refuse_type = refuse_type.upper()

    # API expected 0 prefixed district integers for numbers less than 10
    if district[0] is not '0' and int(district) < 10:
        district = "0" + str(district)

    return borough, refuse_type, district, get_total, 0, []


"""
Query all districts in local db and print the sum of refuse+paper+mgp in tons
"""
def report_total():
    sum = 0
    districts = db['district'].all()

    for d in districts:
        sum += round(d['refusetonscollected']) + round(d['papertonscollected']) + round(d['mgptonscollected'])

    print('Total garbage (refuse, paper, mgp) collected in all districts queried: ' + str(sum) + ' tons')

"""
Initialize the local database with a dummy entry to create the schema needed to store the API calls.
"""
def init_db():
    table = db['district']
    table.upsert(dict(communitydistrict='00', borough='TEST', refusetonscollected=0,
                      papertonscollected=0, mgptonscollected=0), ['communitydistrict'])
"""
- Parse and validate command line arguments
- (Optional) Report total garbage in all districts in saved local db 'sqlite:///mydatabase.db'
- Query the https://dev.socrata.com/foundry/data.cityofnewyork.us/8bkb-pvci endpoint and save entry to local db
- Report the tons of refuse for the specified borough+district or any errors.
"""
def main():
    borough, refuse_type, district, get_total, error_code, error_messages = parse_and_validate_args()

    # running client.py -get_total without an entry will crash the program.
    # initialize the database schema with a dummy entry. (see https://dataset.readthedocs.io/en/latest/index.html
    init_db()

    # if the optional argument is provided, skip the API call and report total in local db
    if get_total:
        report_total()
        exit(0)

    # Display any error messages for invalid CLI's
    if error_code < 0:
        for m in error_messages:
            print(m)
        exit(0)

    results = query_api(borough, district)

    if results.empty:
        tons_collected = 0
    else:
        tons_collected = round(float(results[refuse_type.lower() + garbage_suffix].tolist()[0]))
        upsert(results)

    print(refuse_type + ' collected in ' + borough + ' in district ' + district +
          ' during January 2015: \n' + str(tons_collected) + " tons")

main()

