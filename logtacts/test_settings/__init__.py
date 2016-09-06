from logtacts.settings import *

import fakeredis
CACHES['default']['OPTIONS']['REDIS_CLIENT_CLASS'] = "fakeredis.FakeStrictRedis"