#!/usr/bin/env python

from optparse import OptionParser

import internal
import internal.log

def main():
	sub_commands = ['leaderboard', 'timeofday']
	usage = 'usage: %%prog [options] <%s>' % '|'.join(sub_commands)
	_op = OptionParser(usage=usage)
	_op.add_option('-d', '--directory', default='.', dest='directory', help='Directory of the Git repository to analyze')
	_op.add_option('--dry-run', action='store_true', dest='dryrun', help='Don\'t actually generate graphs, just print data')
	_op.add_option('-c', '--chart', default='bar', dest='chart', help='Type of chart you\'d like (where applicable), (pie, donut, bar)')
	_op.add_option('--before', default=None, dest='before', help='Specify a "before" time frame')
	_op.add_option('--after', default=None, dest='after', help='Speficy an "after" time frame')

	options, args = _op.parse_args()

	if not args or not args[0] in sub_commands:
		print 'You must specify one of the subcommands! (%s)' % ', '.join(sub_commands)
		return
	
	chart = internal.ChartType.Bar
	if options.chart == 'pie':
		chart = internal.ChartType.Pie
	if options.chart == 'donut':
		chart = internal.ChartType.Donut

	kwargs = {'before' : options.before, 'after' : options.after, 'dryrun' : options.dryrun}
	glog = internal.log.GitLog(**kwargs)
	if options.directory:
		glog.directory = options.directory
	glog.load()

	map(lambda x: getattr(glog, x)(chart=chart), args)

if __name__ == '__main__':
	main()
