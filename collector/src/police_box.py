"""
This serves as a 'router' for calling the endpoints within the TARDIS
collector and analytics API.

The TARDIS in Doctor Box is disguised as a police call box, so it seems
like a fitting name given the codenames.
"""

import sys
from selector import

# I hate this... but it'll have to do for now (alenards)
CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)

from configs import ENDPT_PREFIX
from object_lookup import application as lookup
from provenance_agent import application as provenance
from provenance_post import application as prov_post
from object_reg_lookup import application as register

__all__ = ['app']

def say_hello(environ, start_response):
    """
    Test app...
    """
    args, kwargs = environ['wsgiorg.routing_args']
    print args
    start_response("200 OK", [('Content-type', 'text/plain')])
    return ["Hello, %s!" % kwargs['name']]


app = Selector()

# include for smoke testing
app.add('/hello/{name}', GET=say_hello)
app.add(ENDPT_PREFIX + '/hello/{name}', GET=say_hello)

# Change to include a version number as a prefix
app.add(ENDPT_PREFIX + '/lookup[/]', GET=lookup)
app.add(ENDPT_PREFIX +
    '/register/{object_id:word}/{object_name:segment}/' +
    '{object_desc:segment[/{parent_uuid:word}][/]', POST=register)
app.add(ENDPT_PREFIX +
    '/provenance/{uuid:word}/{username}/{service_name}/' +
    '{event_name}/{category_name}[/]', POST=provenance)
app.add(ENDPT_PREFIX +
    '/provenance/{service_name}/{event_name}/{category_name}[/]',
    POST=prov_post)