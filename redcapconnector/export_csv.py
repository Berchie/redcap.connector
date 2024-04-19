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


# export command
@click.command(options_metavar='<options>')
@click.argument(
    "dst",
    type=click.Path(
        exists=True,
        dir_okay=True,
        writable=True
    ),
    default=os.environ['HOME'],
    # help=f"Path to store the CSV files (default:{os.environ['HOME']})"
    metavar='<dst>'
)
def export_csv(dst):
    # display info
    """
    \b
    export the CSV file containing the transferred results.

    \b
    syntax:
        redcon export-csv <dst>[directory path] <options>[-h|--help]
    \b
    Examples:
        \b
        example 1:
            export the csv file to the default location
            $ redcon export-csv
        \b
        example 2:
            export the csv file to document dir/folder
            $ redcon export-csv /home/berchie/Documents
        \b
        example 3:
        help option for export-csv command
        $ redcon export-csv --help
    """

    try:
        # source [src] file or dir
        # src = f"{sys.path[4]}/data/csv/"
        src_dir = os.path.join(os.path.dirname(__file__), "data", "csv")
        list_dir = os.listdir(src_dir)

        # destination [dst] or dir
        # dst = os.path.expanduser(destination)

        f_count = 0

        for csv_file in list_dir:
            if len(list_dir) > 2:
                if csv_file != '__init__.py':
                    if csv_file != 'demo.csv':
                        src = os.path.join(os.path.dirname(__file__), "data", "csv", csv_file)

                        # copy file from src to dst
                        if os.path.isfile(src):
                            cp_info = shutil.copy(src=src, dst=dst)
                            logger.success(f'CSV file has successfully exported. The exported {csv_file} is located at {cp_info}')

                        f_count += 1

        if f_count == 0:
            logger.info('No CSV file was found for export!')

    except Exception as e:
        logger.exception(f"Exception occurred: {e}")


if __name__ == '__main__':
    export_csv(os.environ['HOME'])
