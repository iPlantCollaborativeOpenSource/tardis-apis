"""
This serves as a 'router' for calling the endpoints within the TARDIS
collector and analytics API.

The TARDIS in Doctor Box is disguised as a police call box, so it seems
like a fitting name given the codenames.
"""

import sys
from selector import Selector

# I hate this... but it'll have to do for now (alenards)
CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)

from configs import ENDPT_PREFIX
from object_lookup import application as lookup
from provenance_agent import application as provenance
from provenance_post import application as prov_post
from object_reg_lookup import application as register

# Okay code maintainer - I just want to save you some hassle... mod_wsgi
# is looking for a function or a variable named ``application``. So,
# guess what - don't change this unless you're running this out of
# something less like gunicorn/etc.  Oh... You're welcome.
__all__ = ['application']

def say_hello(environ, start_response):
    """
    Test app...
    """
    args, kwargs = environ['wsgiorg.routing_args']
    print args
    start_response("200 OK", [('Content-type', 'text/plain')])
    return ["Hello, %s!" % kwargs['name']]

# I know - a long variable name, but don't change it - see the above
# message above ``__all__`` for more context...
application = Selector()

# include for smoke testing
application.add('/hello/{name}', GET=say_hello)
application.add(ENDPT_PREFIX + '/hello/{name}', GET=say_hello)

# Change to include a version number as a prefix
application.add(ENDPT_PREFIX + '/lookup[/]', GET=lookup)
application.add(ENDPT_PREFIX +
    '/register/{service_key}/{object_id:segment}/{object_name:segment}/' +
    '{object_desc:segment[/{parent_uuid:word}][/]', POST=register)
application.add(ENDPT_PREFIX +
    '/provenance/{uuid:word}/{username}/{service_name}/' +
    '{event_name}/{category_name}[/]', POST=provenance)
application.add(ENDPT_PREFIX +
    '/provenance/{service_name}/{event_name}/{category_name}[/]',
    POST=prov_post)