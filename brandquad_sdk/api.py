
import platform
import requests

from .entity import EntryPointFactory


__version__ = '1'


class Api(object):
    # User-Agent for HTTP request
    library_details = 'requests %s; python %s' % (requests.__version__, platform.python_version())
    user_agent = 'BrandquadSDK/Brandquad-Python-SDK %s (%s)' % (__version__, library_details)

    def __init__(self, host, token, appid):
        self.response = None
        self.method_mapping = {}

        self.host = host
        self.endpoint = 'api/public_v2/'
        self.token = token
        self.appid = appid

        attr_mapping = {'attributes': 'attributes/',
                        'categories': 'categories/',
                        'files': 'dam/files/',
                        'folders': 'dam/folders/',
                        'products': 'products/'}

        for key in attr_mapping:
            setattr(self, key, EntryPointFactory(self, attr_mapping[key]))

    def compose_url(self, path=None, pk=None):
        url = '{}{}'.format(self.host, self.endpoint)
        if path:
            url = '{}{}'.format(url, path)
        if pk:
            url = '{}{}/'.format(url, pk)

        return url

    def get_response(self, method, data=None, pk=None, path=None, fullurl=None):
        url = self.compose_url(path, pk)
        headers = {'TOKEN': self.token, 'APPID': self.appid}
        try:
            if fullurl:
                response = method(fullurl, headers=headers,)
            else:
                try:
                    response = method(url, data or None, headers=headers, )
                except TypeError:
                    response = method(url, headers=headers, )
        except KeyError:
            raise KeyError('Method %s not allowed' % method)

        self.response = response

        return self.response

