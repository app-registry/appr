from __future__ import absolute_import, division, print_function

import os


class Config(object):
    """ Default configuration """
    DEBUG = False
    APPR_URI = os.getenv('APPR_URI', "http://localhost:5000")


class ProductionConfig(Config):
    """ Production configuration """
    APPR_URI = "http://localhost:5000"
    APPR_BACKEND = 'false'


class DevelopmentConfig(Config):
    """ Development configuration """
    DEBUG = True
    #    APPR_URI = 'https://api.appr.sh'
    APPR_URI = os.getenv('APPR_URI', "http://localhost:5000")
