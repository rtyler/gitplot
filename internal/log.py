import copy
import os
import sys
import time

import internal

from contrib import CairoPlot

def json_decode(s):
	try:
		import cjson
		try:
			return cjson.decode(s)
		except cjson.DecodeError:
			print s
	except ImportError:
		import simplejson
		return simplejson.loads(s)

class GitLog(object):
	directory = '.'
	results = []
	default_directory = directory
	should_graph = True
	__log_format = '''{%x22committer_name%x22 : %x22%cn%x22, %x22committer_email%x22 : %x22%ce%x22, %x22hash%x22 : %x22%H%x22,	%x22abbrev_hash%x22 : %x22%h%x22, %x22committer_date%x22 : %x22%ct%x22, %x22encoding%x22 : %x22%e%x22, %x22subject%x22 : %x22%s%x22, %x22body%x22 : %x22%b%x22, %x22tree_hash%x22 : %x22%T%x22, %x22author_name%x22 : %x22%an%x22, %x22author_email%x22 : %x22%ae%x22, %x22author_date%x22 : %x22%at%x22}GITPLOTEOL'''

	def _get_log_fmt(self):
		return self.__log_format
	log_format = property(fget=_get_log_fmt)

	def _load_full(self):
		cwd = os.getcwd()
		if not self.directory == self.default_directory:
			os.chdir(self.directory)

		results = internal.execute('log', pretty='format:\'%s\'' % self.__log_format)
		os.chdir(cwd)
		return results

	def load(self):
		self.results = [f for f in self._load_full() if f]
		self.results = map(lambda r: json_decode(r), self.results)
		self.results.sort(key=lambda d: d['committer_date'])
	
	def top_committers(self, count=10, filename=None):
		if not self.results:
			self.load()
		counter = {}
		for r in self.results:
			if not counter.get(r['committer_name']):
				counter[r['committer_name']] = 0
			counter[r['committer_name']] += 1

		counter = [(k, v) for k,v in counter.iteritems()]
		counter.sort(key=lambda i: i[1], reverse=True)
		top = counter[:count]

