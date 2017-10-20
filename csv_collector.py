#!/usr/local/bin/python3
'''

This script predicts/detects hate speech for new messages

'''
import requests
import argparse
import sys
import io
import datetime
from calendar import monthrange
import os

import csv
import json
import bs4
import dateparser
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

sys.path.append('confs')
import csv_collector_config

def fetch_data(paths, startdate, enddate):

    ## twitter data collection

    data = ''

    print( 'Collecting Twitter Data from CSV')
    data_cleaned_twitter = []

    for path in paths:

        print( 'Collecting from file: ', path )
        input_file = csv.DictReader(open(path, newline='', encoding='utf-8'))

        for d in input_file:

            print( ' Got this far: ', d)

            data_cleaned_twitter.append( {
                'source' : 'twitter',
                'id' : d['id'],
                'text' : d['text'],
                'created_at' : d['created_at']
            } )

        #d = r.text.split('\n')[1:]
        #data += '\n'.join( d )

    ## fix characterset problems
    #data = data.replace('\x00', '')

        print( 'Total', len( data_cleaned_twitter )  )

    return data_cleaned_twitter

def store_messages(cvsstr, filename):

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    open(outfile, 'w').write(csvstr)

def main(argv):
    # Parse inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--paths', help='list of paths and bin names')
    parser.add_argument('--outdir', help='Directory to store data')
    parser.add_argument('--startdate', help='Startdate as YYYY-MM-DD')
    parser.add_argument('--enddate', help='Enddate as YYYY-MM-DD')

    args = parser.parse_args(argv)

    #TODO: Change it that it get everything unless user sets start and end

    if args.paths is None:
        args.paths = csv_collector_config.paths
    if args.startdate is None:
        startdate = datetime.datetime.now() #.strftime('%Y-%m-%d 00:00:00 utc')
    else:
        startdate = datetime.datetime.strptime(args.startdate, '%Y-%m-%d').date()
    if args.enddate is None:
        enddate = datetime.datetime.now() #.strftime('%Y-%m-%d 23:59:59 utc')
    else:
        enddate = datetime.datetime.strptime(args.enddate, '%Y-%m-%d').date()

    print(startdate, enddate)

    for m in range(startdate.month, enddate.month + 1):
        # Get the day range
        if m == enddate.month:
            days = range(startdate.day, enddate.day + 1)
        else:
            _, days = monthrange(startdate.year, m)
        print(days)

        for d in days:
            startdate_str = '%d-%02d-%02d 00:00:00 utc' % (startdate.year, m, d)
            enddate_str = '%d-%02d-%02d 23:59:59 utc' % (startdate.year, m, d)

            print(startdate_str, enddate_str)

            # Get the data

            response = fetch_data( args.paths, startdate_str , enddate_str )

            # Store results
            # TODO: Store data to database
            outfile = os.path.join('data/', 'incoming',
                                   startdate_str.replace(' ', '_') + '.json')
            if not os.path.exists(os.path.dirname(outfile)):
                os.makedirs(os.path.dirname(outfile))
            json.dump( response, open(outfile, 'w') )


#
if __name__ == "__main__":
    main(sys.argv[1:])
