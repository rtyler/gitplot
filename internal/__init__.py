import os

EOL = 'GITPLOT_EOL'
QUOTE = 'GITPLOT_QUOTE'
DQUOTE = 'GITPLOT_DOUBLEQUOTE'

def execute(cmd, *args, **kwargs):
	kwargs = kwargs or {}
	args = args or []
	kw = ['--%s=%s' % (k,v) for k,v in kwargs.iteritems() if k and v]
	kw.extend(['--%s' % k for k,v in kwargs.iteritems() if k and not v])
	kwargs = kw
	rc = os.popen('git %s %s %s' % (cmd, ' '.join(args), ' '.join(kwargs)))
	rc = rc.read().rstrip()
	return rc.split(EOL)

class ChartType(object):
	Bar = 'Bar'
	Pie = 'Pie'
	Donut = 'Donut'
	
