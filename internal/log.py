import os
import sys
import time

import internal

from contrib import CairoPlot

class GitLog(object):
	directory = '.'
	should_graph = True
	@classmethod
	def committers(cls):
		log_format = '%cn||%ce||%H||%h||%ct'
		cwd = os.getcwd()
		if not cls.directory == '.':
			os.chdir(cls.directory)
			
		results = internal.execute('log', pretty='format:"%s"' % (log_format)) 
		os.chdir(cwd)

		rc = []
		graph_data = {}
		for r in results:
			d = r.split('||')
			name = d[0]
			if not graph_data.get(name):
				graph_data[name] = 0
			graph_data[name] += 1
			rc.append(d)

		if cls.should_graph:
			CairoPlot.donut_plot('committers_%s' % (time.time()), graph_data, 600, 400, gradient=True, inner_radius=0.2, shadow=True)
		return rc
		
