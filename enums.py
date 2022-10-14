import enum

class SEND_MSG_STS(enum.Enum):
    SUCC = 0
    FAIL = 1

class THREAD_MODE(enum.Enum):
    CAMP_LIST = 0
    ZONE_LIST = 1
    SITE_LIST = 2