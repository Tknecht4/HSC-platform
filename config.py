class Config(object):
    DEBUG = True
    SECRET_KEY = '34tk56gj67'
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="tknecht",
        password="echelon123",
        hostname="tknecht.mysql.pythonanywhere-services.com",
        databasename="tknecht$growers",)
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False