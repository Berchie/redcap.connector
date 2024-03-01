# redcap-connect commands -
#   senaite-connect  -> login to senaite api
#   get-results [OPTIONS] -> retrieve the analyses results from senaite lims via api
#   data-import [OPTIONS] -> import the analyses results into REDCap database
#   status [OPTIONS] -> check the transfer of analyses results from senaite limns to REDCap was done or successful
#          [OPTIONS - [--project, -p, 'M19' => MBC, 'P21' => PEDVAC] name of the project,
#                   - [--period, -r, 'today', 'yesterday', 'this-week', 'this-month', 'this-year']
#                       period or date the sample or analysis was published,
#                    - [--days, -d ] number of day(s) back to check the status of the transfer of analysis results
#                   ]


import click
import os
import sys
import json
from .senaite_connect import senaite_connect
from .pull_data_senaite import get_analyses_result
from .importdata import data_import
from .check_status import status


# add the path of the new different folder (the folder from where we want to import the modules)
# sys.path.insert(0, './src')


@click.group('cli')
def cli() -> None:
    """REDCap Connector
    
    \b
    REDCap Connector is a middleware that facilitates the seamless
    integration of SENAITE and REDCap project databases, allowing 
    for the efficient transfer of analysis results. This software 
    acts as a bridge between the two platforms, streamlining the 
    process of data transfer and ensuring the accuracy and integrity 
    of the results.

    \b
    redcap-connector commands -
    senaite-connect  -> login to senaite api
    get-results [OPTIONS] -> retrieve the analyses results from senaite lims via api
    status [OPTIONS] -> check the transfer of analyses results from senaite limns to REDCap was done or successful
           [OPTIONS -> [--project, -p, 'M19' => MBC, 'P21' => PEDVAC] name of the project,
                    -> [--period, -r, 'today', 'yesterday', 'this-week', 'this-month', 'this-year']
                        period or date the sample or analysis was published,
                    -> [--days, -d ] number of day(s) back to check the status of the transfer of analysis results
           ]
    """
    #data-import [OPTIONS] -> import the analyses results into REDCap database
    # _stream = open(document)
    # _dict = json.load(_stream)
    # _stream.close()
    # ctx.obj = _dict


cli.add_command(senaite_connect)
cli.add_command(get_analyses_result)
cli.add_command(status)


if __name__ == '__main__':
    cli()

