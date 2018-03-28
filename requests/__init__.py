# -*- coding: utf-8 -*-

__title__ = 'urllib-requests-adapter'
__version__ = '0.0.1'
__author__ = '@Coffee:matrix.org'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017, 2018 Coffee'

"""
Urllib Requests Adapter

Make simple programs depending on requests[1] work with urllib instead, without
changing a single line of code! Mainly intended for matrix-python-sdk[2], but
that doesn't prevent it from being useful otherwise.

[1]: https://github.com/kennethreitz/requests
[2]: https://github.com/matrix-org/matrix-python-sdk
"""

import urllib.request
import urllib.parse
import urllib.error
import http.client
import json
import os

import requests
import requests.exceptions

capath="/etc/ssl/certs"

import logging
logger = logging.getLogger('urllib-requests-adapter')

def _setup_socks5():
	s5 = os.environ.get('SOCKS5_SERVER', None)
	if not s5: return
	s5s = s5.split(':')
	if len(s5s) != 2:
		logger.warning("Badly formatted environment variable SOCKS5_SERVER: {!r}".format(s5))
		return

	host = s5s[0]
	port = int(s5s[1])

	import socks
	import socket
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, host, port)
	socket.socket = socks.socksocket

DEBUG=False
GLOBAL_TIMEOUT_SECONDS=None

_setup_socks5()

class MethodRequest(urllib.request.Request):
	def __init__(self, url, method="GET", data=None, headers={}, origin_req_host=None, unverifiable=False):
		urllib.request.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
		self.method = method.upper()

	def get_method(self):
	    return self.method

class Response:
	def __init__(self, method, endpoint, params, data=None, headers=None, verify=None, timeout=None):
		if DEBUG: print("New Response with", repr(method), repr(endpoint), repr(params), repr(data), repr(headers), repr(verify), repr(timeout))
		url = endpoint
		if (params is not None):
			url = url + "?" + urllib.parse.urlencode(params)
		if data is not None:
			if isinstance(data, str):
				data = data.encode()
		self._rdata = None
		self.rq = MethodRequest(url, method, data, headers)
		self.timeout_seconds = timeout

	def map_request(self, r):
		self.status_code = r.status
		self.text = r.reason

	def json(self):
		j = json.loads(self._rdata.decode())
		if DEBUG: print("Returning:", repr(j))
		return j

	def __len__(self):
		if self._rdata is None: return 0
		return len(self._rdata)

	def execute(self):
		timeout = self.timeout_seconds
		if timeout is None: timeout = GLOBAL_TIMEOUT_SECONDS
		try:
			if timeout is None:
				r = urllib.request.urlopen(self.rq, capath=capath)
			else:
				r = urllib.request.urlopen(self.rq, None, timeout, capath=capath)
		except urllib.error.HTTPError as e:
			self.status_code = e.code
			self.text = e.msg
			return self
		except (http.client.HTTPException, urllib.error.URLError) as e:
			e2 = exceptions.RequestException("{}.{!r}".format(type(e).__module__, e))
			raise e2
		self._rdata = r.read()
		self.map_request(r)
		r.close()
		return self

def request(method, endpoint, params, data=None, headers=None, verify=None, timeout=None):
	return Response(method, endpoint, params, data=data, headers=headers, timeout=timeout).execute()
