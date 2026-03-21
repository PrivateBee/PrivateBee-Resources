from enum import IntEnum

class GithubInviteCode(IntEnum):
    OK = 0
    CONFIG_MISSING_TOKEN = 1
    USER_NOT_FOUND = 2
    USER_ALREADY_MEMBER = 3
    USER_ALREADY_INVITED = 4
    GITHUB_API_ERROR = 5
    UNKNOWN_ERROR = 99