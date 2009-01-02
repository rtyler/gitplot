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
			raise
	except ImportError:
		import simplejson
		return simplejson.loads(s)

class GitLog(object):
	directory = '.'
	results = []
	default_directory = directory
	should_graph = True
	# OH GOD IT BURNS
	__log_format = '''{%(q)scommitter_name%(q)s : %(q)s%%cn%(q)s, %(q)scommitter_email%(q)s : %(q)s%%ce%(q)s, %(q)shash%(q)s : %(q)s%%H%(q)s,	%(q)sabbrev_hash%(q)s : %(q)s%%h%(q)s, %(q)scommitter_date%(q)s : %(q)s%%ct%(q)s, %(q)sencoding%(q)s : %(q)s%%e%(q)s, %(q)ssubject%(q)s : %(q)s%%s%(q)s, %(q)sbody%(q)s : %(q)s%%b%(q)s, %(q)stree_hash%(q)s : %(q)s%%T%(q)s, %(q)sauthor_name%(q)s : %(q)s%%an%(q)s, %(q)sauthor_email%(q)s : %(q)s%%ae%(q)s, %(q)sauthor_date%(q)s : %(q)s%%at%(q)s}%(eol)s''' % {'q' : internal.DQUOTE, 'eol' : internal.EOL}

	def _get_log_fmt(self):
		return self.__log_format
	log_format = property(fget=_get_log_fmt)

	def _load_full(self):
		cwd = os.getcwd()
		if not self.directory == self.default_directory:
			os.chdir(self.directory)

		results = internal.execute('log', pretty='format:\'%s\'' % self.__log_format)
		os.chdir(cwd)
		results = [r.replace('\\', '\\\\').replace('\"', '\\\"').replace('\'', '\\\'') for r in results]
		results = [r.replace(internal.DQUOTE, '\"') for r in results]
		return results

	def load(self):
		self.results = self._load_full()
		self.results = map(lambda r: r and json_decode(r), self.results)
		self.results = [f for f in self.results if f]
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

		filename = filename or 'top_%d_committers_%s' % (count, time.time())
		data = [c[1] for c in top]
		labels = [c[0] for c in top]
		vlabels = ['0', str(data[0])]
		CairoPlot.bar_plot(filename, data, 600, 200, border=10, grid=True, three_dimension=True, h_labels=labels, v_labels=vlabels) 

