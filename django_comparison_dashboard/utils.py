import urllib.parse

from django.shortcuts import redirect


def redirect_params(url, **params):
    response = redirect(url)
    if params:
        query_string = urllib.parse.urlencode(params)
        response["Location"] += "?" + query_string
    return response
