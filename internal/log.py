import copy
import itertools
import os
import pdb
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
	__log_format = '''%(bol)s{%(q)scommitter_name%(q)s : %(q)s%%cn%(q)s, %(q)scommitter_email%(q)s : %(q)s%%ce%(q)s, %(q)shash%(q)s : %(q)s%%H%(q)s,	%(q)sabbrev_hash%(q)s : %(q)s%%h%(q)s, %(q)scommitter_date%(q)s : %%ct, %(q)sencoding%(q)s : %(q)s%%e%(q)s, %(q)ssubject%(q)s : %(q)s%%s%(q)s, %(q)sbody%(q)s : %(q)s%%b%(q)s, %(q)stree_hash%(q)s : %(q)s%%T%(q)s, %(q)sauthor_name%(q)s : %(q)s%%an%(q)s, %(q)sauthor_email%(q)s : %(q)s%%ae%(q)s, %(q)sauthor_date%(q)s : %%at}%(eol)s''' % {'q' : internal.DQUOTE, 'eol' : internal.EOL, 'bol' : internal.BOL}


	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)

	def _get_log_fmt(self):
		return self.__log_format
	log_format = property(fget=_get_log_fmt)

	def _load_full(self):
		cwd = os.getcwd()
		if not self.directory == self.default_directory:
			os.chdir(self.directory)
		
		kwargs = {'pretty' : 'format:\'%s\'' % self.__log_format, 'numstat' : None, 'split' : internal.BOL}
		if self.before:
			kwargs.update({'before' : '"%s"' % self.before})
		if self.after:
			kwargs.update({'after' : '"%s"' % self.after})
		if self.author:
			kwargs.update({'author' : self.author})
		results = internal.execute('log', **kwargs)
		os.chdir(cwd)
		results = [r.split(internal.EOL) for r in results]
		results = [(r[0].replace('\\', '\\\\').replace('\"', '\\\"').replace('\'', '\\\'').replace(internal.DQUOTE, '\"'), \
				len(r) == 2  and r[1] or '') for r in results]
		return results

	def load(self):
		self.results = self._load_full()
		# Elements in the self.results list should alternate between one line of JSON, and one line of numstats
		rc = []
		for r in self.results:
			if not r[0]:
				continue
			t = json_decode(r[0])
			if len(r) == 2:
				# OW OW OW OW 
				numstat = [n.split('\t') for n in r[1].strip().split('\n')]
				def _numstat_gen(line):
					d = {'added' : 0, 'removed' : 0, 'filename' : line[2], 'binary' : False}
					if line[0] == '-' and line[1] == '-':
						d['binary'] = True
					else:
						d['added'], d['removed'] = int(line[0]),int(line[1])
					return d
				t['numstat'] = map(lambda n: len(n) == 3 and _numstat_gen(n), numstat)
				t['numstat'] = [nm for nm in t['numstat'] if nm]
			else:
				t['numstat'] = []
			rc.append(t)
		self.results = rc
		def timeofday(f):
			return time.strftime('%H:%M', time.localtime(f['committer_date']))
		def handle(f):
			return f['committer_email'].split('@')[0]
		self.results = [f for f in self.results if f and \
			not f.update({'committer_handle' : handle(f), 'committer_timeofday' : timeofday(f)})]
		self.results.sort(key=lambda d: d['author_date'])
	
	def leaderboard(self, width=None, height=None, count=10, filename=None, by_email=True, chart=internal.ChartType.Bar):
		assert width or height
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
		if not top:
			print '===> No data to graph!'
			return

		filename = '%s_leaderboard.png' % (self.filename or time.time())
		def _gen_Bar(t):
			data = [c[1] for c in t]
			labels = [c[0] for c in t]
			vlabels = ['0', str(data[0])]
			CairoPlot.bar_plot(filename, data, width, height, border=10, grid=True, h_labels=labels, v_labels=vlabels) 
		def _gen_Donut(t):
			data = dict([(t[i][0], t[i][1]) for i in xrange(len(t))])
			CairoPlot.donut_plot(filename, data, width, height, gradient=True, shadow=True)
		def _gen_Pie(t):
			data = dict([(t[i][0], t[i][1]) for i in xrange(len(t))])
			CairoPlot.pie_plot(filename, data, width, height, gradient=True)

		try:
			return locals()['_gen_%s' % chart](top)
		except KeyError:
			print 'This function does not support chart type: %s' % chart

	def timeofday(self, width=None, height=None, filename=None, by_email=True, chart=internal.ChartType.Bar):
		assert width or height
		if not self.results:
			self.load()
		results = copy.deepcopy(self.results)
		results.sort(key=lambda d: d['committer_timeofday'])
		filename = '%s_timeofday.png' % (self.filename or time.time())

		def _gen_Bar(r):
			data = {}
			labels = []
			bars = []
			for k,g in itertools.groupby(r, lambda t: (t['committer_timeofday'].split(':')[0], t)):
				hour = k[0]
				if not data.get(hour):
					data[hour] = 0
				data[hour] += 1
			data = [(k,v) for k,v in data.iteritems()]
			data.sort(key=lambda d: d[0])
			upper = 0
			for k,v in data:
				if v > upper:
					upper = v
				bars.append(v)
				labels.append(k)
			vlabels = ['0', str(upper)]
			CairoPlot.bar_plot(filename, bars, width, height, border=10, grid=True, h_labels=labels, v_labels=vlabels) 

		try:
			return locals()['_gen_%s' % chart](results)
		except KeyError:
			print 'This function does not support chart type: %s' % chart

	def churn(self, width=None, height=None, filename=None, chart=internal.ChartType.Bar):
		assert width or height
		if not self.results:
			self.load()
		results = copy.deepcopy(self.results)
		results.reverse()
		filename = '%s_churn.png' % (self.filename or time.time())

		rc = {}
		for commit in results:
			if not commit['numstat']:
				continue
			churn = []
			for file in commit['numstat']:
				if file['binary']:
					continue
				churn.append( (file['added'], file['removed'], file['filename']) )

			author = commit['committer_handle']
			if not rc.get(author):
				rc[author] = {'commits' : 0, 'files' : [], 'added' : 0, 'removed' : 0}

			rc[author]['commits'] += 1
			rc[author]['files'].extend([f[2] for f in churn])
			added = map(lambda c: c[0], churn)
			removed = map(lambda c: c[1], churn)
			rc[author]['added'] += added and reduce(lambda x,y: x+y, added) or 0
			rc[author]['removed'] += removed and reduce(lambda x,y: x+y, removed) or 0
		
		d = []
		for k,r in rc.iteritems():
			d.append( (k, r['commits'], r['files'], abs(r['added']-r['removed']) / r['commits'] ) )
			#print '%s touched %d files, +%s, -%s lines (total: %s, net: %s)' % (k, r['distinct_files'], r['added'], r['removed'], r['added']+r['removed'], r['added']-r['removed'])
			#print '\t Average net-change per commit: %.2f lines' % ( abs(r['added']-r['removed']) / r['commits'] )

		def _gen_Bar(data):
			vlabels = ['0']
			def _average_files(gdata):
				return len(gdata[2]) / gdata[1]
			data.sort(key=lambda d: d[1], reverse=True)
			data = data[:10]
			bars = [[k[3], _average_files(k)] for k in data]
			labels = [k[0] for k in data]
			vlabels.extend([str(d[0]) for d in bars])
			vlabels = [f for f in vlabels if int(f)]
			vlabels.sort(key=lambda t: int(t))
			vlabels = ['0', vlabels[-1]]
			CairoPlot.bar_plot(filename, bars, width, height, border=10, grid=True, h_labels=labels, v_labels=vlabels) 

		try:
			return locals()['_gen_%s' % chart](d)
		except KeyError:
			print 'This function does not support chart type: %s' % chart

