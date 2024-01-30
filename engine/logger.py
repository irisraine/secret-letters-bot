import logging.config
import os


def init_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging_settings = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s][%(levelname)s] : %(message)s',
                'datefmt': '%d-%m-%Y %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'logs/bot.log',
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
        }
    }
    logging.config.dictConfig(logging_settings)
