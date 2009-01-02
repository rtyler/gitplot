import os
import sys
import time

import internal

from contrib import CairoPlot

def json_decode(s):
	try:
		import cjson
		return cjson.decode(s)
	except ImportError:
		import simplejson
		return simplejson.loads(s)

class GitLog(object):
	directory = '.'
	default_directory = directory
	should_graph = True
	__log_format = '''{"committer_name" : "%cn", "committer_email" : "%ce", "hash" : "%H",	"abbrev_hash" : "%h", "committer_date" : "%ct", "encoding" : "%e"}'''

	def _get_log_fmt(self):
		return self.__log_format
	log_format = property(fget=_get_log_fmt)

	def _load_full(self):
		cwd = os.getcwd()
		if not self.directory == self.default_directory:
			os.chdir(self.directory)

		results = internal.execute('log', pretty="format:'%s'" % self.__log_format)
		os.chdir(cwd)
		return results

	def load(self):
		self.results = self._load_full()
		self.results = map(lambda r: json_decode(r), self.results)
		print self.results

		
