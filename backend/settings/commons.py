import pytz

SUCCESS_STATUS = 'SUCCESS'
PENDING_STATUS = 'PENDING'
FAILURE_STATUS = 'FAILURE'
RETRY_STATUS = 'RETRY'
REVOKE_STATUS = 'REVOKED'
TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
TAG = 'tag'
PHONE_PREFIX = 'cell_provider_prefix'
FILTER_TYPE = [
    (TAG, 'user tag'),
    (PHONE_PREFIX, 'phone prefix'),
]
