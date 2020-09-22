import environ

ROOT_DIR = environ.Path(__file__) - 3 # (safe_relay_service/config/settings/base.py - 3 = safe-relay-service/)
APPS_DIR = ROOT_DIR.path('safe_relay_service')

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)
DOT_ENV_FILE = env('DJANGO_DOT_ENV_FILE', default=None)
if READ_DOT_ENV_FILE or DOT_ENV_FILE:
    DOT_ENV_FILE = DOT_ENV_FILE or '.env'
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(DOT_ENV_FILE)))

# GENERAL

DEBUG = env.bool('DJANGO_DEBUG', False)
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# DATABASES

psql_url = 'psql://' + env('POSTGRES_USER') + ':' + env('POSTGRES_PASSWORD') + '@db:5432/' + env('POSTGRES_DATABASE_RELAYER')

DATABASES = {
    'default': env.db('RELAYER_DATABASE', default=psql_url),
}

DATABASES['default']['ATOMIC_REQUESTS'] = True

# URLS

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# APPS

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'corsheaders',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
]

LOCAL_APPS = [
    'safe_relay_service.relay.apps.RelayConfig',
    'safe_relay_service.tokens.apps.TokensConfig',
    'safe_relay_service.gas_station.apps.GasStationConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# STATIC

STATIC_ROOT = '/usr/share/nginx/html/relayer';

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA

MEDIA_ROOT = str(APPS_DIR('media'))
MEDIA_URL = '/media/'

# TEMPLATES

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# FIXTURES

FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# ADMIN

ADMIN_URL = r'^admin/'

ADMINS = [
    ("""Circles""", 'webmaster@joincircles.net'),
]

MANAGERS = ADMINS

# Celery

INSTALLED_APPS += [
    'safe_relay_service.taskapp.celery.CeleryConfig',
    'django_celery_beat',
]

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='django://')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

# Django REST Framework

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'EXCEPTION_HANDLER': 'safe_relay_service.relay.views.custom_exception_handler',
}

# LOGGING

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'ignore_check_url': {
            '()': 'safe_relay_service.relay.utils.IgnoreCheckUrl'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] [%(processName)s] %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'celery.worker.strategy': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True
        },
        'django.server': {  # Gunicorn uses `gunicorn.access`
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
            'filters': ['ignore_check_url'],
        },
    }
}

REDIS_URL = env('RELAYER_REDIS_URL', default='redis://localhost:6379/0')

# ETHEREUM

ETH_HASH_PREFIX = env('ETH_HASH_PREFIX', default='ETH')
ETHEREUM_NODE_URL = env('ETHEREUM_NODE_ENDPOINT', default=None)
ETHEREUM_TRACING_NODE_URL = env('ETHEREUM_TRACING_NODE_URL', default=ETHEREUM_NODE_URL)

GAS_STATION_NUMBER_BLOCKS = env('GAS_STATION_NUMBER_BLOCKS', default=300)

# Safe
# ------------------------------------------------------------------------------
SAFE_FUNDER_PRIVATE_KEY = env('SAFE_FUNDER_PRIVATE_KEY', default=None)

# Maximum ether (no wei) for a single transaction (security limit)

SAFE_FUNDER_MAX_ETH = env.int('SAFE_FUNDER_MAX_ETH', default=0.1)
SAFE_FUNDING_CONFIRMATIONS = env.int('SAFE_FUNDING_CONFIRMATIONS', default=3)  # Set to at least 3

# Master Copy Address of Safe Contract
SAFE_CONTRACT_ADDRESS = env('SAFE_ADDRESS', default='0x' + '0' * 39 + '1')

SAFE_V1_0_0_CONTRACT_ADDRESS = env('SAFE_V1_0_0_CONTRACT_ADDRESS', default='0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A')
SAFE_V0_0_1_CONTRACT_ADDRESS = env('SAFE_V0_0_1_CONTRACT_ADDRESS', default='0x8942595A2dC5181Df0465AF0D7be08c8f23C93af')
SAFE_VALID_CONTRACT_ADDRESSES = set(env.list('SAFE_VALID_CONTRACT_ADDRESSES',
                                             default=['0xaE32496491b53841efb51829d6f886387708F99B',
                                                      '0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A'
                                                      '0x8942595A2dC5181Df0465AF0D7be08c8f23C93af',
                                                      '0xAC6072986E985aaBE7804695EC2d8970Cf7541A2'])
                                    ) | {SAFE_CONTRACT_ADDRESS,
                                         SAFE_V1_0_0_CONTRACT_ADDRESS,
                                         SAFE_V0_0_1_CONTRACT_ADDRESS}

SAFE_PROXY_FACTORY_ADDRESS = env('PROXY_FACTORY_ADDRESS', default='0x' + '0' * 39 + '2')

SAFE_PROXY_FACTORY_V1_0_0_ADDRESS = env('SAFE_PROXY_FACTORY_V1_0_0_ADDRESS',
                                        default='0x12302fE9c02ff50939BaAaaf415fc226C078613C')
SAFE_DEFAULT_CALLBACK_HANDLER = env('SAFE_DEFAULT_CALLBACK_HANDLER',
                                    default='0xd5D82B6aDDc9027B22dCA772Aa68D5d74cdBdF44')

# If FIXED_GAS_PRICE is None, GasStation will be used
FIXED_GAS_PRICE = env.int('FIXED_GAS_PRICE', default=None)
SAFE_TX_SENDER_PRIVATE_KEY = env('SAFE_TX_SENDER_PRIVATE_KEY', default=None)

SAFE_CHECK_DEPLOYER_FUNDED_DELAY = env.int('SAFE_CHECK_DEPLOYER_FUNDED_DELAY', default=1 * 30)
SAFE_CHECK_DEPLOYER_FUNDED_RETRIES = env.int('SAFE_CHECK_DEPLOYER_FUNDED_RETRIES', default=10)
SAFE_FIXED_CREATION_COST = env.int('SAFE_FIXED_CREATION_COST', default=None)
SAFE_ACCOUNTS_BALANCE_WARNING = env.int('SAFE_ACCOUNTS_BALANCE_WARNING', default=200000000000000000)  # 0.2 Eth
SAFE_TX_NOT_MINED_ALERT_MINUTES = env('SAFE_TX_NOT_MINED_ALERT_MINUTES', default=10)

NOTIFICATION_SERVICE_URI = env('NOTIFICATION_SERVICE_URI', default=None)
NOTIFICATION_SERVICE_PASS = env('NOTIFICATION_SERVICE_PASS', default=None)

TOKEN_LOGO_BASE_URI = env('TOKEN_LOGO_BASE_URI', default='')
TOKEN_LOGO_EXTENSION = env('TOKEN_LOGO_EXTENSION', default='.png')

# CACHES

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('RELAYER_REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

# CIRCLES

CIRCLES_HUB_ADDRESS = env('HUB_ADDRESS', default='0x' + '0' * 39 + '2')

GRAPH_NODE_EXTERNAL = env('GRAPH_NODE_EXTERNAL', default='')
SUBGRAPH_NAME = env('SUBGRAPH_NAME', default='')

MIN_TRUST_CONNECTIONS = env('MIN_TRUST_CONNECTIONS', default=3)

# DOCKER

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']
INTERNAL_IPS += [ip[:-1] + '1' for ip in ips]
