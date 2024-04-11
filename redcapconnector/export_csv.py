import os
import shutil
import sys
import click
from loguru import logger
from redcapconnector.config.log_config import handlers

# setting up the logging
logger.configure(
    handlers=handlers,
)


example_context = """
        \b
        example 1:
        ---------
            # export the csv file to the default location
            redcon export-csv
        \b
        example 2:
        ---------
            # export the csv file to document dir/folder
            redcon export-csv -o /home/berchie/Documents
        \b   
        example 3:
        ---------
        # help option for export_csv command
        redcon export-csv --help
"""


# export command
@click.command(epilog=example_context)
@click.option(
    "-o", "--destination",
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
                    logger.success(f'CSV file has successfully exported. The exported csv file is located at {cp_info}')
            else:
                logger.info('No CSV file was found for export!')

    except Exception as e:
        logger.exception("Exception occurred: %s", str(e))


if __name__ == '__main__':
    export_csv("")
