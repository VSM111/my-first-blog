from django.shortcuts import render
QueryDict
from django.conf import settings
from cursesite.functions.functions import render_template

ALLOWED_BROWSERS = (
	('Firefox', 1.5),
	('Opera', 9),
	('MSIE', 7),
	('Safari', 85),
)

def check_browser(agent):
	
	for b in ALLOWED_BROWSERS:
		loc = agent.find(b[0])
		if loc != -1:
			start = loc+len(b[0])+1
			end = agent.find(' ', start)
			if end != -1:
				version = agent[start:end]
			else:
				version = agent[start:]
			if version == '':
				version = '2.0'
			elif version[-1] == ';':
				version = version[0:-1]
			version = version.split('.')
			version = "%s.%s" % (version[0].split(')')[0], ''.join(version[1:]).split(',')[0].split('+')[0].split('u')[0].split('a')[0])
			if float(version) < float(b[1]):
				valid = False
			else:
				valid = True
			ec = {'browser_version': version, 'browser': b[0], 'valid': valid}
			return ec

	return {'browser': agent, 'browser_version': '', 'valid': True}

class ValidateBrowser(object):
	def process_response(self, request, response):
		if '_verify_browser' in request.COOKIES or request.META['HTTP_USER_AGENT'] == 'Python-urllib/1.16' or request.GET.get('skipcheck', False) or request.META['HTTP_USER_AGENT'].find('Googlebot') != -1:
			return response
			
		agent = request.META['HTTP_USER_AGENT']
		ec = check_browser(agent)	
		if '_verified' in request.GET:
			ec.update({'no_cookies': True})
			
		# Redirect URL
		if 'PATH_INFO' in request.META:
			url = request.META['PATH_INFO']
		elif 'REQUEST_URI' in request.META:
			url = request.META['REQUEST_URI']
		else:
			url = '/'
		q = QueryDict(request.META['QUERY_STRING'])
		if '_verified' not in q:
			q = q.copy() # to make it mutable
			q.update({'_verified': '1'})
		url += "?%s" % q.urlencode()
		
		ec.update({'url': url})
		
		response = render_template(request, 'browsercheck.html', ec)
		response.set_cookie('_verify_browser', '1', max_age=60*60*24*30, domain=settings.SESSION_COOKIE_DOMAIN)
		return response

# Create your views here.
