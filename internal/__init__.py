import os

BOL = 'GITPLOT_BOL'
EOL = 'GITPLOT_EOL'
QUOTE = 'GITPLOT_QUOTE'
DQUOTE = 'GITPLOT_DOUBLEQUOTE'

def execute(cmd, *args, **kwargs):
	kwargs = kwargs or {}
	split = kwargs.pop('split', True)
	args = args or []
	kw = ['--%s=%s' % (k,v) for k,v in kwargs.iteritems() if k and v]
	kw.extend(['--%s' % k for k,v in kwargs.iteritems() if k and not v])
	kwargs = kw
	rc = os.popen('git %s %s %s' % (cmd, ' '.join(args), ' '.join(kwargs)))
	rc = rc.read().rstrip()
	if split == True:
		return rc.split(EOL)
	return rc.split(split)

class ChartType(object):
	Bar = 'Bar'
	Pie = 'Pie'
	Donut = 'Donut'
	
