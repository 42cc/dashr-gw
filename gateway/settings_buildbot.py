from settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gateway',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = ['dash-gw.s.42cc.co']

ENCRYPTED_FIELDS_KEYDIR = os.path.join(BASE_DIR, '../fieldkeys')
