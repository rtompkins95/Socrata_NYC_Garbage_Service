# Ryan Tompkins - PragyaSystems DSNY RESTful API DEMO

## Introduction


> This is a Python3 RESTful client designed to report the garbage collected in NYC. The dataset available for public use and located at https://dev.socrata.com/foundry/data.cityofnewyork.us/ with resource key 8bkb-pvci.

> It uses an opensource database framework called 'Dataset' that can be found here at https://dataset.readthedocs.io/en/latest/index.html. Every API call will report the data to the command line and record the entry in a local database file ('sqlite:///mydatabase.db' by default)

## Code Samples

> python3 client.py -b Bronx -t PAPER -d 9

> python3 client.py -b BROOKLYN -t mgp -d 01

> python3 client.py -get_total


>>The first two use cases will query the endpoint with the specified attributes and save a copy of the entry to disk (note: that all types of refuse are saved to local db, but only the argument provided for -t will be reported on the command line)

>>The third call is used to report the total paper, refuse, and mgp for every district that has been queried during the clients usage. To reset the database, run 'rm mydatabase.db && python3 client.py -get_total'


## Installation

 make sure to install these packages before running:
> pip install pandas

> pip install sodapy

> pip install dataset

After this, ensure Python3 is up-to-date and that client.py and config.py are both in your working directory. 
