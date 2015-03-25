#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sts=4 sw=4 et

import platform
import os
import sys
import json
import base64
import urllib
import hmac
import hashlib

try:
    import argparse # `easy_install argparse` or `pip install argparse`
except:
    print 'Cannot find library "argparse"!'
    print 'Please do either:'
    print '    sudo apt-get install python-argparse'
    print '    sudo easy_install argparse'
    print '    sudo pip install argparse'
    print '    Go to https://pypi.python.org/pypi/argparse'
    sys.exit(1)

try:
    import requests
except:
    print 'Cannot find library "requests"!'
    print 'Please do either:'
    print '    sudo apt-get install python-requests'
    print '    sudo easy_install requests'
    print '    sudo pip install requests'
    print '    Go to http://docs.python-requests.org/en/latest/user/install/#get-the-code'
    sys.exit(1)

try:
    import pygments
    import pygments.lexer
    import pygments.lexers
    import pygments.formatters
except:
    print 'Cannot find library "Pygments"!'
    print 'Please do either:'
    print '    sudo apt-get install python-pygments'
    print '    sudo easy_install Pygments'
    print '    sudo pip install pygments'
    print '    Go to http://pygments.org/docs/installation/'
    sys.exit(1)



class Logger:
    DEFAULT = 1
    ERROR = 0
    WARNING = 1
    INFO = 2
    VERBOSE = 3
    def __init__(self, level):
        self.level = level
    def log(self, level, msg, *format_args):
        if level > self.level:
            return
        if len(format_args) > 0:
            msg = msg % format_args
        print msg
    def error(self, msg, *format_args):
        self.log(Logger.ERROR, msg, *format_args)
    def warn(self, msg, *format_args):
        self.log(Logger.WARNING, msg, *format_args)
    def info(self, msg, *format_args):
        self.log(Logger.INFO, msg, *format_args)
    def verbose(self, msg, *format_args):
        self.log(Logger.VERBOSE, msg, *format_args)

# Class taken from https://github.com/jkbr/httpie/blob/6f64b437b7228151b89c45c40e0ec0c2d99a78c4/httpie/output.py#L299
class HTTPLexer(pygments.lexer.RegexLexer):
    """Simplified HTTP lexer for Pygments.

    It only operates on headers and provides a stronger contrast between
    their names and values than the original one bundled with Pygments
    (:class:`pygments.lexers.text import HttpLexer`), especially when
    Solarized color scheme is used.

    """
    name = 'HTTP'
    aliases = ['http']
    filenames = ['*.http']
    tokens = {
        'root': [
            # Request-Line
            (r'([A-Z]+)( +)([^ ]+)( +)(HTTP)(/)(\d+\.\d+)',
             pygments.lexer.bygroups(
                 pygments.token.Name.Function,
                 pygments.token.Text,
                 pygments.token.Name.Namespace,
                 pygments.token.Text,
                 pygments.token.Keyword.Reserved,
                 pygments.token.Operator,
                 pygments.token.Number
             )),
            # Response Status-Line
            (r'(HTTP)(/)(\d+\.\d+)( +)(\d{3})( +)(.+)',
             pygments.lexer.bygroups(
                 pygments.token.Keyword.Reserved,  # 'HTTP'
                 pygments.token.Operator,  # '/'
                 pygments.token.Number,  # Version
                 pygments.token.Text,
                 pygments.token.Number,  # Status code
                 pygments.token.Text,
                 pygments.token.Name.Exception,  # Reason
             )),
            # Header
            (r'(.*?)( *)(:)( *)(.+)', pygments.lexer.bygroups(
                pygments.token.Name.Attribute,  # Name
                pygments.token.Text,
                pygments.token.Operator,  # Colon
                pygments.token.Text,
                pygments.token.String  # Value
            ))
        ]
    }

config_cached = None
def getConfig():
    global config_cached
    if config_cached is None:
        if platform.system() == 'Windows':
            folder = os.path.expandvars(r'%APPDATA%\\wonderpush')
        else:
            folder = os.path.expanduser('~/.wonderpush')
        folder = os.environ.get('WONDERPUSH_CONFIG_DIR', folder)
        try:
            f = open(os.path.join(folder, 'rest.conf'), 'rt')
            config_cached = json.load(f)
            f.close()
        except IOError:
            config_cached = {}
    return config_cached

def getDefaultArgs():
    return getConfig().get('arguments', [])

def getProfileArgs(profile):
    return getConfig().get('profiles', {}).get(profile, {}).get('arguments', [])

def parseArgs(argv = None, **kwargs):
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            conflict_handler='resolve',
            description='REST client for the WonderPush platform.',
            epilog='''\
You can create a configuration file in "~/.wonderpush/" or
"%APPDATA%\\wonderpush" named "rest.conf" to define default arguments
and profiles.

The file structure is as follows:
    {
      "arguments": [],    # default arguments, always prepended to your
                          # command line
      "profiles": {
        "default": {      # default profile
          "arguments": [] # arguments to prepend after the default arguments
        },
        ...               # you can define your own profiles
      }
    }

Available styles are:\n  - ''' + '\n  - '.join(list(pygments.styles.get_all_styles())))
    parser.add_argument('-p', '--profile', action='store', type=str, default='default', dest='profile', help='Profile to use (default: %(default)s)')
    parser.add_argument('-h', '--host', action='store', type=str, default='api.wonderpush.com', dest='host', help='Host to contact (default: %(default)s)')
    parser.add_argument('-v', '--verbose', action='count', dest='verbose_level', help='Controls verbosity level')
    parser.add_argument('-q', '--quiet', action='store_const', const=0, dest='verbose_level', help='Mute, except for exceptional errors')
    parser.add_argument('--no-ssl-verify', action='store_false', dest='ssl_verify', help='Disable verification of SSL certificate')
    parser.add_argument('--no-format', action='store_false', dest='format', help='Disable formatting the output')
    parser.add_argument('--no-highlight', action='store_false', dest='highlight', help='Disable highlighting the output')
    parser.add_argument('--style', action='store', type=str, default='default', dest='style', help='Pygments style to use while highlighting (default: %(default)s)')
    parser.add_argument('-c', '--client-id', action='store', type=str, dest='client_id', help='Your client id')
    parser.add_argument('-s', '--client-secret', action='store', type=str, dest='client_secret', help='Your client secret')
    parser.add_argument('-a', '--access-token', action='store', type=str, dest='access_token', help='The OAuth access token to use')
    parser.add_argument('-i', '--sid', action='store', type=str, dest='sid', help='The session id to use')
    parser.add_argument('method', type=str, nargs='?', default='GET', help='The HTTP method to use: GET, POST, PUT, DELETE (default: %(default)s)')
    parser.add_argument('path', type=str, help='The path to query. Eg.: /v1/players/me')
    parser.add_argument('headers', metavar='header:value', type=str, nargs='*', help='Additional headers.') # Eats up all positional arguments
    parser.add_argument('params', metavar='param=value', type=str, nargs='*', help='Additional query parameters. Eg.: lang=en')
    if argv is None:
        argv = sys.argv[1:]
    argv_toParse = argv[:]
    argv_toParse.extend(['--%s' % key.replace('_', '-') for key, value in kwargs.iteritems() if value == True])
    argv_toParse.extend(['--%s=%s' % (key.replace('_', '-'), value) for key, value in kwargs.iteritems() if type(value) != bool])
    args = parser.parse_args(getDefaultArgs() + argv_toParse)
    if args.profile is not None:
        # Reparse arguments by now adding the given profile's arguments
        args = parser.parse_args(getDefaultArgs() + getProfileArgs(args.profile) + argv_toParse)
    if args.verbose_level is None:
        args.verbose_level = Logger.DEFAULT # map "no modifier" to level 1
    elif args.verbose_level >= 1:
        args.verbose_level += 1 # hence shift the count of '-v's
    args.logger = Logger(args.verbose_level)
    if args.method.upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        # Shift arguments to add method=GET
        args.headers.insert(0, args.path)
        args.path = args.method
        args.method = 'GET'
    else:
        args.method = args.method.upper()
    if len(args.path) >= 1 and args.path[0] == '/':
        args.path = args.path[1:]
    args.url = 'https://%s/%s' % ( args.host, args.path )
    # Parse headers and params
    headers = {}
    params = {}
    for p in args.headers:
        colon = p.find(':')
        equal = p.find('=')
        if colon >= 0 and (equal < 0 or (equal >= 0 and colon < equal)):
            dest = headers
            split = ':'
        else:
            dest = params
            split = '='
        p = p.split(split, 1)
        if len(p) == 1:
            p.append('')
        k,v = p
        if k in params:
            args.logger.verbose('Parameter "%s" already given', k)
        dest[k] = v
    args.headers = headers
    args.params = params
    if args.sid is not None:
        args.params['sid'] = args.sid
    if args.client_id is not None:
        args.params['clientId'] = args.client_id
    if args.access_token is not None:
        args.params['accessToken'] = args.access_token
    if args.client_secret is not None:
        args.headers['X-WonderPush-Authorization'] = 'WonderPush sig="%s", meth="0"' % percent_encode(base64.standard_b64encode(sign(args)))
    return args

def sign(args):
    params = '&'.join(sorted(['%s=%s' % (percent_encode(k), percent_encode(v)) for k,v in args.params.iteritems()]))
    body = ''
    fields = []
    fields.append(args.method.upper())
    fields.append(args.url)
    fields.append(params)
    fields.append(body)
    fields = '&'.join([percent_encode(field) for field in fields])
    args.logger.verbose('Signature before HMAC_SHA1: %s', fields)
    return hmac.new(args.client_secret, fields, hashlib.sha1).digest()

def percent_encode(s):
    return urllib.quote(s, '~')

def formatRequest(args, request):
    headers = ''.join(['%s: %s\n' % (h,v) for h,v in request.headers.iteritems()])
    http = '%s %s HTTP/1.1\n%s' % (request.method, request.path_url, headers)
    try:
        lexer = HTTPLexer()
        if args.highlight:
            formatter = pygments.formatters.get_formatter_by_name('terminal256', style=args.style)
            http = pygments.highlight(http, lexer, formatter)
    except:
        pass # Cannot do highlighting
    return http

def formatResponse(args, response):
    headers = None
    try:
        headers = ['%s: %s\n' % (h,v) for h,v in response.raw._original_response.msg._headers]
    except AttributeError:
        headers = ['%s\n' % h.strip() for h in response.raw._original_response.msg.headers]
    headers = ''.join(headers)
    http = 'HTTP/%s %d %s\n%s' % ('.'.join(str(response.raw.version)), response.status_code, response.reason, headers)
    try:
        lexer = HTTPLexer()
        if args.highlight:
            formatter = pygments.formatters.get_formatter_by_name('terminal256', style=args.style)
            http = pygments.highlight(http, lexer, formatter)
    except:
        pass # Cannot do highlighting
    lexerName = 'html'
    body = response.text
    if response.json is not None:
        try:
            if args.format:
                body = json.dumps(response.json(), indent=4, ensure_ascii=False, check_circular=False)
            lexerName = 'json'
        except ValueError:
            # Cannot do proper JSON indentation
            pass
    try:
        lexer = pygments.lexers.get_lexer_by_name(lexerName)
        if args.highlight:
            formatter = pygments.formatters.get_formatter_by_name('terminal256', style=args.style)
            body = pygments.highlight(body, lexer, formatter)
    except:
        pass # Cannot do highlighting
    return (http, body)

def query(argv = None, **kwargs):
    args = parseArgs(argv, **kwargs)
    request = requests.Request(method=args.method, url=args.url, headers=args.headers, params=args.params)
    request = request.prepare()
    args.logger.info(formatRequest(args, request))
    response = requests.Session().send(request, verify=args.ssl_verify)
    http, body = formatResponse(args, response)
    args.logger.info('%s', http)
    print body.encode('utf-8')
    return 0



def main():
    return query(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())
