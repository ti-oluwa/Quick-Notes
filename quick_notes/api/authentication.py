from rest_framework.authentication import TokenAuthentication


class AccessTokenAuthentication(TokenAuthentication):
    '''Custom `TokenAuthentication` class'''
    keyword = "Bearer"