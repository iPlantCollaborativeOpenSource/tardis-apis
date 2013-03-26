"""
Simple test for validation of attributes associated with provenance
logging.
"""

# Ugly hack to allow absolute import from the root folder
# whatever its name is. Please forgive the heresy.
if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir_

    path.append(dir_(path[0]))
    __package__ = "tests"
# So what street corner did that I pick that up from?
#
#   Check out ``canary.py`` for proper credit...

from provenance_agent import ProvTuple, validate

#
# uuid => (r'^[0-9]+$')
# others => (r'^[A-Za-z0-9\-_]+$')
#


def test_tuple_without_required():
    """
    Force the failured of the ``has_required_arguments()`` on ProvTuple.

    Currently, ``has_required_arguments()`` is used in the definition of
    ``validate()`` (at least when this test was written).

    The required fields for a request for provenance logging are:

    - ``uuid``
    - ``service_name``
    - ``category_name``
    - ``event_name``
    - ``username``

    A call to has_required_arguments() will verify that none of these
    attributes are ``None``.

    In the constructor, none of the arguments are optional.  Therefore,
    all newly instantiated ``ProvTuple`` objects are valid until any of
    the attributes are mucked with or manipulated.
    """
    prov = ProvTuple(9090909090, 'DE', 'view', 'list-dir', 'tester',
                '10.0.0.1')
    assert prov.has_required_arguments()

    tmp = prov.uuid
    prov.uuid = None
    assert not prov.has_required_arguments()

    prov.uuid = tmp
    tmp = prov.service_name
    prov.service_name = None
    assert not prov.has_required_arguments()

    prov.service_name = tmp
    tmp = prov.category_name
    prov.category_name = None
    assert not prov.has_required_arguments()

    prov.category_name = tmp
    tmp = prov.event_name
    prov.event_name = None
    assert not prov.has_required_arguments()

    prov.event_name = tmp
    tmp = prov.username
    prov.username = None
    assert not prov.has_required_arguments()

    prov.username = None
    prov.event_name  = None
    prov.category_name = None
    prov.service_name = None
    prov.uuid = None
    assert not prov.has_required_arguments()


def test_simple_validate_default_case():
    """
    Verify that a simple set of default values works.

    See if example values for the required attributes is accepted by the
    ``validate()`` method.
    """
    prov = ProvTuple('9090909090', 'DE', 'view', 'list-dir', 'tester',
                '10.0.0.1')
    assert prov.has_required_arguments()
    is_valid, details = validate(prov)
    print details
    assert is_valid

    prov = ProvTuple('9999999999', 'DE-kahn_v', 'v_i-e_w-0', '-list_dir-90',
        'tester', '10.0.0.1')
    assert prov.has_required_arguments()
    is_valid, details = validate(prov)
    print details
    assert is_valid


def test_fail_validate_for_uuid():
    """
    Verify that UUIDs that contain non-numerals fail.
    """
    prov = ProvTuple('0xC0FFEE', 'DE', 'view', 'list-dir', 'tester',
                '10.0.0.1')
    assert prov.has_required_arguments()
    is_valid, details = validate(prov)
    print details
    assert not is_valid


def test_all_arguments_validate_default_case():
    """
    Verify that a set of all values works.
    """
    prov = ProvTuple('9090909090', 'DE', 'view', 'list-dir', 'tester',
                '10.0.0.1')
    prov.proxy_username = 'de-rods'
    # this will likely fail.
    prov.version = '1.0.1'
    assert prov.has_required_arguments()
    is_valid, details = validate(prov)
    print details
    assert is_valid

    prov.version = '5.5.4rc'
    is_valid, details = validate(prov)
    print details
    assert is_valid

    prov.version = '5.5.4-rc'
    is_valid, details = validate(prov)
    print details
    assert is_valid


def test_fail_validate_for_any_field():
    """
    Verify that regex is catching invalid characters for all other
    fields.
    """
    prov = ProvTuple('65099091929', 'DWAP', 'create', 'make-dir', 'tester',
                '10.0.66.1')
    assert prov.has_required_arguments()
    tmp = prov.service_name
    prov.service_name = 'D%6^'
    is_valid, details = validate(prov)
    print details
    assert not is_valid

    prov.service_name = tmp
    tmp = prov.category_name
    prov.category_name = 'cre&'
    is_valid, details = validate(prov)
    print details
    assert not is_valid

    prov.category_name = tmp
    tmp = prov.event_name
    prov.event_name = 'make-*'
    is_valid, details = validate(prov)
    print details
    assert not is_valid

    prov.event_name = tmp
    tmp = prov.username
    prov.username = 'ndy$'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.username = '@ndy'
    is_valid, details = validate(prov)
    print details
    assert not is_valid


    prov.username = tmp
    prov.proxy_username = 'user@aweso.me'
    is_valid, details = validate(prov)
    print details
    assert not is_valid

    prov.proxy_username = None
    prov.version = '5.5.4:rc'
    is_valid, details = validate(prov)
    print details
    assert not is_valid

    prov.version = '5.5.4;rc'
    is_valid, details = validate(prov)
    print details
    assert not is_valid

    prov.version = '5.5.4 (rc)'
    is_valid, details = validate(prov)
    print details
    assert not is_valid

    prov.version = None

    tmp = prov.event_name
    prov.event_name = 'solve-{rubix}'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = 'make|rubix'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = 'solve\\kjlkj'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = 'solve/rubics'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = 'life=rubics'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = 'dalek+artoo'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = '`reality`'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = '~millions'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = 'millions?'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = '<millions>'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
    prov.event_name = 'millions, /really'
    is_valid, details = validate(prov)
    print details
    assert not is_valid
