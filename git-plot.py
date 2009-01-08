#!/usr/bin/env python

from optparse import OptionParser

import internal
import internal.log

def main():
	sub_commands = ['leaderboard', 'timeofday', 'churn']
	usage = 'usage: %%prog [options] <%s>' % '|'.join(sub_commands)
	_op = OptionParser(usage=usage)
	_op.add_option('-d', '--directory', default='.', dest='directory', help='Directory of the Git repository to analyze')
	_op.add_option('--dry-run', action='store_true', dest='dryrun', help='Don\'t actually generate graphs, just print data')
	_op.add_option('-c', '--chart', default='bar', dest='chart', help='Type of chart you\'d like (where applicable), (pie, donut, bar)')
	_op.add_option('--before', default=None, dest='before', help='Specify a "before" time frame')
	_op.add_option('--after', default=None, dest='after', help='Specify an "after" time frame')
	_op.add_option('--author', default=None, dest='author', help='Specify the author to generate the statistics for')
	_op.add_option('-y', '--height', default=450, dest='height', help='Height of generated images')
	_op.add_option('-x', '--width', default=800, dest='width', help='Width of generated images')
	_op.add_option('-f', '--prefix', default=None, dest='filename', help='Prefix for generated image files')

	options, args = _op.parse_args()

	if not args or not args[0] in sub_commands:
		print 'You must specify one of the subcommands! (%s)' % ', '.join(sub_commands)
		return
	
	chart = internal.ChartType.Bar
	if options.chart == 'pie':
		chart = internal.ChartType.Pie
	if options.chart == 'donut':
		chart = internal.ChartType.Donut

	kwargs = {'before' : options.before, 'after' : options.after, 'dryrun' : options.dryrun, 'filename' : options.filename,
					'author' : options.author}
	glog = internal.log.GitLog(**kwargs)
	if options.directory:
		glog.directory = options.directory
	glog.load()

	map(lambda x: getattr(glog, x)(chart=chart, height=int(options.height), width=int(options.width)), args)

if __name__ == '__main__':
	main()
