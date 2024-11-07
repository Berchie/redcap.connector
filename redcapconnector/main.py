import click
import redcapconnector.senaite_connect as senaite_connect
import redcapconnector.pull_data_senaite as get_result
import redcapconnector.check_status as cs
import redcapconnector.export_csv as ec
import redcapconnector.smart_result_transfer as srt

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group('cli', context_settings=CONTEXT_SETTINGS)
@click.version_option(
    '0.1.4',
    '-v', '--version',
    prog_name="redcap-connector"
)
def cli() -> None:
    """redcap-connector
    
    \b
    redcap-connector is a middleware that facilitates the seamless
    integration of SENAITE and REDCap project databases, allowing 
    for the efficient transfer of analysis results. This software 
    acts as a bridge between the two platforms, streamlining the 
    process of data transfer and ensuring the accuracy and integrity 
    of the results.
    """


cli.add_command(senaite_connect.senaite_connect)
cli.add_command(get_result.transfer_result)
cli.add_command(srt.transfer_smart_result)
cli.add_command(cs.status)
cli.add_command(ec.export_csv)

# descriptive of the middleware that has been committed out
# \b
# syntax:
#     redcon COMMAND [ARGS] [OPTIONS]
#
# \b
# COMMAND:
# -----------
# \b
# senaite-connect  -> login to SENAITE LIMS
#
# \b
# transfer-result [OPTIONS] -> transfer analysis results from SENAITE LIMS to REDCap
#
# \b
# status [OPTIONS] -> check whether transfer of analysis results from
#                     SENAITE LIMS to REDCap was done or successful
#
# \b
# export_csv [OPTIONS] -> export the CSV file containing the transferred results
#
# \b
# [ARGS]
# ------------
#     dst =>  Path to store the CSV files
#
# \b
# [OPTIONS]:
# -------------
#     --project, -p, ['M19' => MBC, 'P21' => PEDVAC]  => name of the project
# \b
#     --period ['today', 'yesterday', 'this-week', 'this-month', 'this-year'] => period or date the sample or analysis was published,
# \b
#     --days, -d => number of day(s) back to check the status of the transfer of analysis results,

if __name__ == '__main__':
    # max_content_width=120
    cli()
