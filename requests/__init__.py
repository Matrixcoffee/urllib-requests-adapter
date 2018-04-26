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

import pprint
import sys
import urllib.request
import urllib.parse
import urllib.error
import http.client
import json
import os
import socket

import requests
import requests.exceptions

CAFILE = None
CAPATH = None
CONTEXT = None

import logging
logger = logging.getLogger('urllib-requests-adapter')

RequestException = requests.exceptions.RequestException
MissingSchema = requests.exceptions.MissingSchema

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

def _setup_tls():
	# Ensure at least _something_ is configured.
	# If not, we might not be verifying certificates and
	# thus make insecure connections.

	# Defaults will not work with Python 3.2. If you need it to work there,
	# explicitly set either CAFILE or CAPATH after importing this module.

	global CAFILE, CAPATH, CONTEXT
	if CAFILE is None and CAPATH is None and CONTEXT is None:
		import ssl
		CONTEXT = ssl.create_default_context()
		# Overkill all the overkill
		CONTEXT.verify_mode = ssl.CERT_REQUIRED

def _get_tls_parms():
	# Return a dict suitable for passing to urlopen() as dictionary arguments
	# via **.
	_setup_tls()
	parms = {}
	if CAFILE is not None: parms['cafile'] = CAFILE
	if CAPATH is not None: parms['capath'] = CAPATH
	if CONTEXT is not None: parms['context'] = CONTEXT
	return parms

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
		if DEBUG: print("New Response with", repr(method), repr(endpoint), repr(params), repr(data), repr(headers), repr(verify), repr(timeout), file=sys.stderr)
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
		if DEBUG: print("map_request:", repr(r.status), repr(r.reason), file=sys.stderr)

	def json(self):
		j = json.loads(self._rdata.decode())
		if DEBUG: pprint.pprint(j, stream=sys.stderr)
		return j

	def __len__(self):
		if self._rdata is None: return 0
		return len(self._rdata)

	def execute(self):
		timeout = self.timeout_seconds
		if timeout is None: timeout = GLOBAL_TIMEOUT_SECONDS
		try:
			if timeout is None:
				r = urllib.request.urlopen(self.rq, **_get_tls_parms())
			else:
				r = urllib.request.urlopen(self.rq, None, timeout, **_get_tls_parms())
		except urllib.error.HTTPError as e:
			self.status_code = e.code
			self.text = e.msg
			return self
		except (http.client.HTTPException, urllib.error.URLError, socket.timeout) as e:
			e2 = exceptions.RequestException("{}.{!r}".format(type(e).__module__, e))
			raise e2
		self._rdata = r.read()
		if DEBUG: print("Response._rdata set to:", repr(self._rdata), file=sys.stderr)
		self.map_request(r)
		r.close()
		return self

def request(method, endpoint, params, data=None, headers=None, verify=None, timeout=None):
	return Response(method, endpoint, params, data=data, headers=headers, timeout=timeout).execute()


class Session:
	request = staticmethod(request)
