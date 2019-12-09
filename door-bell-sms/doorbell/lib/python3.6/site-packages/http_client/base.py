from io import BytesIO
from six import iteritems
import pycurl


class Request(object):
    def __init__(self, save_to=None, **options):
        self.save_to = save_to
        self.options = options
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)
        self.content = BytesIO()
        self.headers = BytesIO()
        self.curl.setopt(pycurl.HEADERFUNCTION, self.headers.write)
        if self.save_to is None:
            self.curl.setopt(pycurl.WRITEFUNCTION, self.content.write)
        else:
            self.file_to_write = open(self.save_to, "wb")
            self.curl.setopt(pycurl.WRITEFUNCTION, self.file_to_write.write)
        for (key, value) in iteritems(self.options):
            if key == "proxytype":
                if value == "socks4":
                    self.curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
                elif value == "socks5":
                    self.curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
            else:
                self.curl.setopt(getattr(pycurl, key.upper()), value)


class Response(object):
    def __init__(self, request):
        self.save_to = request.save_to
        self.options = request.options
        self.content = request.content.getvalue().decode("utf-8", errors="ignore")
        self.headers = request.headers.getvalue().decode("utf-8", errors="ignore")
        self.status_code = request.curl.getinfo(request.curl.RESPONSE_CODE)
        self.total_time = request.curl.getinfo(request.curl.TOTAL_TIME)


def fetch(save_to=None, **options):
    request = Request(save_to, **options)
    request.curl.perform()
    response = Response(request)
    request.curl.close()
    if hasattr(request, "file_to_write"):
        request.file_to_write.close()
    return response


def fetchmany(*requests):
    curl_multi = pycurl.CurlMulti()
    for request in requests:
        curl_multi.add_handle(request.curl)
    while True:
        r, n = curl_multi.perform()
        if n == 0:
            break
    responses = [Response(request) for request in requests]
    for request in requests:
        curl_multi.remove_handle(request.curl)
        request.curl.close()
        if hasattr(request, "file_to_write"):
            request.file_to_write.close()
    curl_multi.close()
    return responses
