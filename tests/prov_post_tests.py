# Ugly hack to allow absolute import from the root folder
# whatever its name is. Please forgive the heresy.
if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir_

    path.append(dir_(path[0]))
    __package__ = "tests"
# So what street corner did that I pick that up from?
#
#   Evpok mentioned it on StackOverflow and I thought it was better than other
#   ideas I had for getting code importable for testing and I don't know that
#   these scripts will be "a module" until a framework is used.
#
#   In short, thanks to Evpok - it'll help get me testing this code.
#
# url: http://stackoverflow.com/questions/6323860/
#           sibling-package-imports/6466139#6466139

import json
from nose.tools import raises
from webob import Request
from provenance_post import _get_post_body

# Require information for logging a provenance object:
# ``uuid``, ``service_name``, ``category_name``, ``event_name``,
# ``username``, ``request_ip`` (request IP address)

# Optional arguments can be set by attribute:
# ``proxy_username``, ``event_data``, ``track_history``,
# ``track_history_code``, ``created_date``, ``version``


def test_get_for_form_encoding_with_uuid():
    """
    Verify that an HTTP POST with form-encoded creates correct tuple...

    We're
    Look at the docstring for ``ProvTuple`` in the ``provenance_agent``
    module for the required attributes and optional attributes.
    """
    req = Request.blank('/provenance/DE/view/list-dir')
    req.method = 'POST'
    req.body = 'uuid=89797989898989&service_name=DE&category_name=view' + \
                '&event_name=list-dir&username=lenards'
    req.remote_addr = '10.0.6.50'
    req.environ['CONTENT_LENGTH'] = str(len(req.body))
    req.environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'

    prov, json_data, webstatus = _get_post_body(req)

    print json_data
    print webstatus

    assert prov is not None
    assert prov.created_date is not None
    assert prov.uuid == '89797989898989'
    assert prov.service_name == 'DE'
    assert prov.category_name == 'view'
    assert prov.event_name == 'list-dir'
    assert prov.username == 'lenards'
    assert prov.request_ipaddress == '10.0.6.50'

    # We expect that ``json_data`` & ``webstatus`` will be ``None``
    assert json_data is None
    assert webstatus is None

    req.body = 'uuid=89797989898989&service_name=DE&category_name=view' + \
                '&event_name=list-dir&username=lenards&' + \
                'proxy_username=de-irods&event_data=%20%20hjhkjhkjhkjhkjhk' + \
                '&version=1.0'
    req.environ['CONTENT_LENGTH'] = str(len(req.body))

    prov, json_data, webstatus = _get_post_body(req)

    print json_data
    print webstatus

    assert prov is not None
    assert prov.uuid == '89797989898989'
    assert prov.service_name == 'DE'
    assert prov.category_name == 'view'
    assert prov.event_name == 'list-dir'
    assert prov.username == 'lenards'
    assert prov.request_ipaddress == '10.0.6.50'
    assert prov.version == '1.0'
    assert prov.proxy_username == 'de-irods'
    assert prov.event_data == '  hjhkjhkjhkjhkjhk'

    # We expect that ``json_data`` & ``webstatus`` will be ``None``
    assert json_data is None
    assert webstatus is None

    req.body = 'uuid=89797989898989&service_name=DE&category_name=view' + \
                '&event_name=list-dir&username=lenards&' + \
                'proxy_username=de-irods&event_data=%20%20hjhkjhkjhkjhkjhk' + \
                '&version=1.0&track_history=1&track_history_code=' + \
                '9031954fc3a2afd8f0943972a6d4bba2'
    req.environ['CONTENT_LENGTH'] = str(len(req.body))

    prov, json_data, webstatus = _get_post_body(req)

    print json_data
    print webstatus

    assert prov is not None
    assert prov.track_history == '1'
    assert prov.track_history_code == '9031954fc3a2afd8f0943972a6d4bba2'

    # We expect that ``json_data`` & ``webstatus`` will be ``None``
    assert json_data is None
    assert webstatus is None


def test_get_for_form_encoded_without_uuid():
    """
    Verify tuple construction  when body is form-urlencoded without a
    ``uuid`` value.
    """

    req = Request.blank('/provenance/DE/view/list-dir')
    req.method = 'POST'
    req.body = 'service_name=DE&category_name=view&event_name=list-dir&' + \
                'username=lenards&service_object_id=650&object_name=fileb' + \
                '&object_desc=a%20really%20useful%20file'
    req.remote_addr = '10.0.6.50'
    req.environ['CONTENT_LENGTH'] = str(len(req.body))
    req.environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'

    prov, json_data, webstatus = _get_post_body(req)

    print json_data
    print webstatus

    assert prov is not None
    assert prov.uuid is None
    assert prov.service_name == 'DE'
    assert prov.category_name == 'view'
    assert prov.event_name == 'list-dir'
    assert prov.username == 'lenards'
    assert prov.request_ipaddress == '10.0.6.50'
    assert prov.object_name == 'fileb'
    assert prov.object_desc == 'a really useful file'

    # We expect that ``json_data`` & ``webstatus`` will be ``None``
    assert json_data is None
    assert webstatus is None

    req.body = 'service_name=DE&category_name=view&event_name=list-dir&' + \
                'username=lenards&service_object_id=650&object_name=fileb' + \
                '&object_desc=a%20really%20useful%20file&parent_uuid=' + \
                '898989898989898987'
    req.environ['CONTENT_LENGTH'] = str(len(req.body))

    prov, json_data, webstatus = _get_post_body(req)

    assert prov.uuid is None
    assert prov.parent_uuid == '898989898989898987'

    # We expect that ``json_data`` & ``webstatus`` will be ``None``
    assert json_data is None
    assert webstatus is None


@raises(KeyError)
def test_get_for_form_encoded_with_missing_key():
    """
    Verify that a key error is thrown when a required value is missing
    from the HTTP POST body.
    """
    req = Request.blank('/provenance/DE/view/list-dir')
    req.method = 'POST'
    req.body = 'uuid=89797989898989&service_name__=DE&category_name=view' + \
                '&event_name=list-dir&username=lenards&protoculture=true'
    # note that "extra data", like the above ``protoculture`` will just
    # be ignored by the ``_get_post_body()`` method.
    req.environ['CONTENT_LENGTH'] = str(len(req.body))
    req.environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'

    prov, json_data, webstatus = _get_post_body(req)
    # everything goes BOOOOOM!  Missing required key...


@raises(ValueError)
def test_verify_json_loads_throws_value_error():
    """
    Canary... demonstrate that invalid JSON will cause ``json.loads()``
    to throw a ``ValueError``.
    """
    fake_body = 'uuid=89797989898989&service_name__=DE&category_name=view' + \
                '&event_name=list-dir&username=lenards&protoculture=true'
    # load the body and see if it's "valid" JSON
    json.loads(fake_body)

def test_get_for_json_body_required():
    """
    Verify that an HTTP POST body containing JSON is loaded correctly.
    """
    req = Request.blank('/provenance/DE/view/list-dir')
    req.method = 'POST'
    req.body = '{ "uuid": "7872424154123412", "service_name" : "DWAAWA", ' + \
                '"category_name": "view", "event_name": "list-root-dir", ' + \
                '"username": "rhunter" }'
    req.remote_addr = '10.0.6.50'
    req.environ['CONTENT_LENGTH'] = str(len(req.body))
    req.environ['CONTENT_TYPE'] = 'application/json'

    # load the body and see if it's "valid" JSON
    json.loads(req.body)

    prov, json_data, webstatus = _get_post_body(req)

    print json_data
    print webstatus

    assert prov is not None
    assert prov.created_date is not None
    assert prov.uuid == '7872424154123412'
    assert prov.service_name == 'DWAAWA'
    assert prov.category_name == 'view'
    assert prov.event_name == 'list-root-dir'
    assert prov.username == 'rhunter'
    assert prov.request_ipaddress == '10.0.6.50'

    # We expect that ``json_data`` & ``webstatus`` will be ``None``
    assert json_data is None
    assert webstatus is None

    req.body = '{ "uuid": "7872424154123412", "service_name" : "DWAAWA", ' + \
                '"category_name": "view", "event_name": "list-root-dir", ' + \
                '"username": "rhunter", "proxy_username": "de-irods", ' + \
                '"event_data": "skull%20squadron%20forever", "version": "1.0" }'
    req.environ['CONTENT_LENGTH'] = str(len(req.body))

    # load the body and see if it's "valid" JSON
    json.loads(req.body)

    prov, json_data, webstatus = _get_post_body(req)

    print json_data
    print webstatus

    assert prov is not None
    # webob.Request isn't URL decoding the JSON data, so we expect %20's/etc.
    assert prov.event_data == 'skull%20squadron%20forever'
    assert prov.version == '1.0'
    assert prov.proxy_username == 'de-irods'
