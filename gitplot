#!/usr/bin/env python

from optparse import OptionParser

import internal
import internal.log

def main():
	print "===> Starting Git Plot"
	_op = OptionParser()
	_op.add_option('-d', '--directory', dest='directory', help='Directory of the Git repository to analyze')
	_op.add_option('--dry-run', action='store_true', dest='dryrun', help='Don\'t actually generate graphs, just print data')
	_op.add_option('-c', '--chart', default='bar', dest='chart', help='Type of chart you\'d like (where applicable), (pie, donut, bar)')

	options, args = _op.parse_args()
	
	chart = internal.ChartType.Bar
	if options.chart == 'pie':
		chart = internal.ChartType.Pie
	if options.chart == 'donut':
		chart = internal.ChartType.Donut
	
	glog = internal.log.GitLog(dryrun=options.dryrun)
	if options.directory:
		glog.directory = options.directory
	glog.load()
	glog.top_committers(chart=chart)


if __name__ == '__main__':
	main()
