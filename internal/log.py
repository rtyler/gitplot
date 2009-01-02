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


	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)

	def _get_log_fmt(self):
		return self.__log_format
	log_format = property(fget=_get_log_fmt)

	def _load_full(self):
		cwd = os.getcwd()
		if not self.directory == self.default_directory:
			os.chdir(self.directory)

		results = internal.execute('log', pretty='format:\'%s\'' % self.__log_format)
		os.chdir(cwd)
		results = [r.replace('\\', '\\\\').replace('\"', '\\\"').replace('\'', '\\\'').replace(internal.DQUOTE, '\"') for r in results]
		return results

	def load(self):
		self.results = self._load_full()
		self.results = map(lambda r: r and json_decode(r), self.results)
		self.results = [f for f in self.results if f and not f.update({'committer_handle' : f['committer_email'].split('@')[0]})]
		self.results.sort(key=lambda d: d['author_date'])
	
	def top_committers(self, count=10, filename=None, by_email=True, chart=internal.ChartType.Bar):
		if not self.results:
			self.load()
		counter = {}
		for r in self.results:
			name = r['committer_handle']
			if not by_email:
				name = r['committer_name']
			if not counter.get(name):
				counter[name] = 0
			counter[name] += 1

		counter = [(k, v) for k,v in counter.iteritems()]
		counter.sort(key=lambda i: i[1], reverse=True)
		top = counter[:count]

		if self.dryrun:
			print top
			return

		filename = filename or 'top_%d_committers_%s' % (count, time.time())
		def _gen_Bar(t):
			data = [c[1] for c in t]
			labels = [c[0] for c in t]
			vlabels = ['0', str(data[0])]
			CairoPlot.bar_plot(filename, data, 600, 200, border=10, grid=True, three_dimension=True, h_labels=labels, v_labels=vlabels) 
		def _gen_Donut(t):
			data = dict([(t[i][0], t[i][1]) for i in xrange(len(t))])
			CairoPlot.donut_plot(filename, data, 600, 400, gradient=True, shadow=True)
		def _gen_Pie(t):
			data = dict([(t[i][0], t[i][1]) for i in xrange(len(t))])
			CairoPlot.pie_plot(filename, data, 600, 400, gradient=True)

		try:
			return locals()['_gen_%s' % chart](top)
		except KeyError:
			print 'This function does not support chart type: %s' % chart

