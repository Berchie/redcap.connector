import logging.config
import os
import shutil
import sys
import click
import yaml
from redcapconnector.setup_logging import setup_logging


# import the customize logger YAML dictionary configuration file
# logging any error or any exception to a log file
# with open(f'{sys.path[4]}/redcapconnector/config/config_log.yaml', 'r') as f:
#     config = yaml.safe_load(f.read())
#     logging.config.dictConfig(config)


# setting up the logging
setup_logging(os.path.join(os.path.dirname(__file__), "log", "redcap_connector.log"))

logger = logging.getLogger(__name__)


# export command
@click.command()
@click.option(
    "-d", "--destination",
    default=os.environ['HOME'],
    help=f"Path to store the CSV files (default:{os.environ['HOME']})"
)
def export_csv(destination):
    try:
        # source [src] file or dir
        # src = f"{sys.path[4]}/data/csv/"
        src_dir = os.path.join(os.path.dirname(__file__), "redcapconnector", "data", "csv")
        list_dir = os.listdir(src_dir)

        # destination [dst] file or dir
        dst = os.path.expanduser(destination)

        for csv_file in list_dir:
            if len(list_dir) > 2:
                if csv_file != '__ini__.py' or csv_file != 'demo.csv':
                    src = os.path.join(sys.path[4], "redcapconnector", "data", "csv", csv_file)

                    # copy file from src to dst
                    cp_info = shutil.copy(src=src, dst=dst)
                    logger.info(f'CSV file has successfully exported. The exported csv file is located at {cp_info}')
            else:
                click.secho('No CSV file was found for export!', fg='blue')

    except Exception as e:
        logger.exception("Exception occurred: %s", str(e))
