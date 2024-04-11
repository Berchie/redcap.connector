import click
import redcapconnector.senaite_connect as senaite_connect
import redcapconnector.pull_data_senaite as get_result
import redcapconnector.check_status as cs
import redcapconnector.export_csv as ec


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
    redcapconnector commands -
    senaite-connect  -> login to senaite api
    get-results [OPTIONS] -> retrieve the analyses results from senaite lims via api
    status [OPTIONS] -> check the transfer of analyses results from senaite limns to REDCap was done or successful
           [OPTIONS -> [--project, -p, 'M19' => MBC, 'P21' => PEDVAC] name of the project,
                    -> [--period, -r, 'today', 'yesterday', 'this-week', 'this-month', 'this-year']
                        period or date the sample or analysis was published,
                    -> [--days, -d ] number of day(s) back to check the status of the transfer of analysis results
           ]
    """


cli.add_command(senaite_connect.senaite_connect)
cli.add_command(get_result.transfer_result)
cli.add_command(cs.status)
cli.add_command(ec.export_csv)

if __name__ == '__main__':
    cli()
