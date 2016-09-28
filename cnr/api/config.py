import os


class Config(object):
    """ Default configuration """
    DEBUG = False
    CNR_URI = os.getenv('CNR_URI', "http://localhost:5000")


class ProductionConfig(Config):
    """ Production configuration """
    CNR_URI = "http://localhost:5000"
    CNR_BACKEND = 'false'


class DevelopmentConfig(Config):
    """ Development configuration """
    DEBUG = True
#    CNR_URI = 'https://api.cnr.sh'
    CNR_URI = os.getenv('CNR_URI', "http://localhost:5000")
