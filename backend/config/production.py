# this is a template for production, can be used for new customers. this is the only file we need to change per customer
# rest of code should be able to be re-used and only one code-based needed

SQLALCHEMY_DATABASE_URI = 'mysql://test:test@localhost/test'
DEBUG = False
PROPAGATE_EXCEPTIONS = True
SECRET_KEY = 'some-random-secret'
LOGGING_INSTANCE = 'DM_MOO'
#LOGGING_LOCATION = '/home/<user>/<instance>/'
SALT = '$2b$12$UpJgNdF2KVESnuNax/IH6.'
