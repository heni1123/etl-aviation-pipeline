import logging
import logging.config
import os

class LoggerConfig:
    @staticmethod
    def setup_logging() -> None:
        log_directory = 'logs'
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        log_file_path = os.path.join(log_directory, 'etl_process.log')

        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'level': logging.INFO,
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'formatter': 'standard',
                    'level': logging.INFO,
                    'filename': log_file_path,
                },
            },
            'loggers': {
                'etl_logger': {
                    'handlers': ['console', 'file'],
                    'level': logging.INFO,
                    'propagate': False,
                },
            },
        }

        logging.config.dictConfig(logging_config)