# -*- coding: utf-8 -*-

__title__ = 'fake-requests'
__version__ = '0.0.1'
__author__ = '@Coffee:matrix.org'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 Coffee'

"""
Requests mini clone

"Fake" library pretending to be requests, but implementing the bare minimum necessary for matrix-python-sdk, wrapping standard urllib.
"""

import urllib.request
import urllib.parse
import json

capath="/etc/ssl/certs"

try:
	# For TAILS. See README.md on how to install socks.py
	import socks
	import socket
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
	socket.socket = socks.socksocket
except:
	pass

DEBUG=False

class MethodRequest(urllib.request.Request):
	def __init__(self, url, method="GET", data=None, headers={}, origin_req_host=None, unverifiable=False):
		urllib.request.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
		self.method = method.upper()

	def get_method(self):
	    return self.method

class Response:
	def __init__(self, method, endpoint, params, data=None, headers=None, verify=None):
		if DEBUG: print("New Response with", repr(method), repr(endpoint), repr(params), repr(data), repr(headers), repr(verify))
		url = endpoint
		if (params is not None):
			url = url + "?" + urllib.parse.urlencode(params)
		if data is not None:
			if isinstance(data, str):
				data = data.encode()
		self._rdata = None
		self.rq = MethodRequest(url, method, data, headers)

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
		r = urllib.request.urlopen(self.rq, capath=capath)
		self._rdata = r.read()
		self.map_request(r)
		r.close()
		return self

def request(method, endpoint, params, data=None, headers=None, verify=None):
	return Response(method, endpoint, params, data=data, headers=headers).execute()
