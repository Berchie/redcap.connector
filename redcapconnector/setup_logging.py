import os
import logging
import logging.config
import yaml


def setup_logging(log_file):
    with open(os.path.join(os.path.dirname(__file__), 'config', "config_log.yaml"), "r") as cf:
        config = yaml.safe_load(cf.read())
        # Replacing parameter in the config with provide value
        config["handlers"]["file"]["filename"] = log_file

    # print(config)
    logging.config.dictConfig(config)

    logger = logging.getLogger(__name__)

    return logger


if __name__ == '__main__':
    setup_logging(os.path.join(os.path.dirname(__file__), "log", "redcap_connector.log"))
