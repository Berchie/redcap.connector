import os
import sys


log_file_path = os.path.join(os.path.dirname(__file__), os.pardir, "log", 'redcap_connector.log')

handlers = [
    dict(sink=sys.stderr),
    dict(
        sink=log_file_path,
        format="{time:DD-MM-YYYY HH:mm:ss}   {name}     {level}: {message}",
        enqueue=True,
        rotation="2 minutes",
        retention="3 minutes"
    )
]


# format="{level.icon} {time:DD-MM-YYYY HH:mm:ss} | {level} | {message}"
# os.pardir ("..")
