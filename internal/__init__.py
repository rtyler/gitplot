import os

EOL = 'GITPLOT_EOL'
QUOTE = 'GITPLOT_QUOTE'
DQUOTE = 'GITPLOT_DOUBLEQUOTE'

def execute(cmd, *args, **kwargs):
	kwargs = kwargs or {}
	args = args or []
	kwargs = ['--%s=%s' % (k,v) for k,v in kwargs.iteritems()]
	rc = os.popen('git %s %s %s' % (cmd, ' '.join(args), ' '.join(kwargs)))
	rc = rc.read().rstrip()
	return rc.split(EOL)
	
