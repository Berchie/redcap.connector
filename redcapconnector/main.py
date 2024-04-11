import click
import redcapconnector.senaite_connect as senaite_connect
import redcapconnector.pull_data_senaite as get_result
import redcapconnector.check_status as cs
import redcapconnector.export_csv as ec


class bold_text:
    BOLD = "\033[1m"


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

cli_examples = """
\b
Examples:  
  example 1:
      login into SENAITE
      $ redcon senaite-connect

  example 2:
      Transferring the results
      $ redcon transfer-result -p M19 --period today

  example 3:
      check the status of yesterday's transfer
      $ redcon status --days 1
"""


@click.group('cli', context_settings=CONTEXT_SETTINGS)
@click.version_option(
    '0.1.0',
    '-v', '--version',
    prog_name="redcap-connector"
)
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
    redcon COMMAND [ARGS] [OPTIONS]

    \b
    ---------------------------------------------------
    redcapconnector commands
    ---------------------------------------------------
    \b
    senaite-connect  -> login to senaite api

    \b
    transfer-result [OPTIONS] -> retrieve the analyses results
                                 from senaite lims via api

    \b
    status [OPTIONS] -> check the transfer of analyses results from
                        senaite limns to REDCap was done or successful

    \b
    export_csv [OPTIONS] -> export the result csv file

    \b
    [ARGS]
    ------------
        --project, -p, ['M19' => MBC, 'P21' => PEDVAC]  => name of the project

    \b
    [OPTIONS]:
    -------------
        --period ['today', 'yesterday', 'this-week', 'this-month', 'this-year'] => period or date the sample or analysis was published,
    \b
        --days, -d => number of day(s) back to check the status of the transfer of analysis results,
    \b
        -o, --destination =>  Path to store the CSV files
    """


cli.add_command(senaite_connect.senaite_connect)
cli.add_command(get_result.transfer_result)
cli.add_command(cs.status)
cli.add_command(ec.export_csv)

if __name__ == '__main__':
    cli(max_content_width=120, epilog=cli_examples)
