
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0mgys*rp#qgel!@--h4tqxg52lr)9l5n=c7y3j3f)hv*b@rmc#'

# SECURITY WARNING: don't run with debug turned on in production!
# False in production
DEBUG = False
TEMPLATE_DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'db.sqlite3',
#     }
# }


# mysql://bf329ce360970a:ebb86e20@eu-cdbr-west-01.cleardb.com/heroku_bfee0306a62d481?reconnect=true

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'heroku_bfee0306a62d481',
        'USER': 'bf329ce360970a',
        'PASSWORD': 'ebb86e20',
        # 'HOST': 'localhost',
        # 'PORT': '3306',
    }
}


# Update database configuration with $DATABASE_URL.
import dj_database_url

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)