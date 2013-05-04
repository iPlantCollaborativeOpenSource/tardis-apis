Collector API
=============

"Just before his head died, his last words were 'Death is but a door. Time is
but a window. I'll be back.' "

"Kill the body, the head will die. Ali-Frazier fight."

# Endpoints

For the sake of discussion, let us assume that there is an installed instance of the Collector API running under the domain ``http://tardis-dev`` on port ``8000``.  Also, we talking about the v1.4 Alpha release, so the version in URLs will be ``1.4a``.  This will mean that our exmaples will be using the following:

>
> http://tardis-dev:8000/1.4a/
>

## Object Lookup (UUID)

This service will return the UUID associated, or "registered" an object. This will *NOT* register the object.

Call returns UUID if the object is found else, returns 404.

### Parameters

_service_key_ -- required (schema reference: defined in the ``Service`` )
_object_id_   -- required

#### Usage

###### looking up an object...

Using Python:

>>> import requests
>>> query = {'service_key': 'KAHN-Test', 'object_id': 'TT:6556-8'}
>>> r = request.get("http://tardis-dev:8000/1.4a/lookup/", params=query)
>>> r = requests.get("http://tardis-dev:8000/1.4a/lookup/", params=query)
>>> r.text
u'{\n    "UUID": "330063643242663936"\n}'
>>>

Using cURL:

>
> $ curl -X GET "http://tardis-dev:8000/1.4a/lookup?service_key=KAHN-Test&object_id=TT%A6556-8"
> {
>    "UUID": "330063643242663936"
> }
>

###### looking up an object that doesn't exist...

> $ curl -X GET "http://tardis-dev:8000/1.4a/lookup?service_key=KAHN-Test&object_id=TT6556-8"
> {
>    "Status": "Failed",
>    "Details": "Object does not exist"
> }

###### not providing the required parameters...

>$ curl -v -X GET "http://tardis-dev:8000/1.4a/lookup?service_key=KAHN-Test"

This currently responds with an  HTTP 500 Internal Server Error


## Object Registration

This call provides an easy registration process. It will perform the lookup, if the object does not exists, it will register the object return the uuid value.
Call returns UUID if the object is found else, returns 404.

Registration now requires a ``service_key`` in addition to the ``object_id``.  The ``object_id``
is an identifier defined within the domain of the calling application.  To ensure that those identifiers do not collide with other calling applications, the ``service_key`` is used to _scope_ or "namespace" all registered objects.

### Endpoint

### Parameters

_service_key_ -- required
_object_id_ -- required
_object_name_ -- required
_object_desc_ -- required
_parent_uuid_ -- optional

##### Usage

######

Using Python:

>>> r = requests.post("http://tardis-dev:8000/1.4a/register/KAHN-Test/TT66678/example/description/")
>>> r.text
u'{\n    "UUID": "330480398003867648"\n}'
>>> r.status_code
200
>>> r.json()
{u'UUID': u'330480398003867648'}
>>>

Using cURL:

> $ curl -X POST "http://tardis-dev:8000/1.4a/register/KAHN-Test/TT66678/example/description/"
>
> {"UUID": "330480398003867648"}

Note - that's the same UUID because when a calling application retries to re-register an object, they will be given the previously associated UUID for the { `service_key`, `object_id` } unique combination (eerrr.. composite key).

Editorial Note - I never got the ``parent_uuid`` field to be properly constrained to the ``uuid`` column within the ``Object`` table.  So if you submit values for ``parent_uuid``, they'll just be accepted (well, they have to be numbers... but there is no verification that they exist).

## Committing Provenance

I don't want to use the term "log" or "logging" here because the topics of ``provenance`` and ``logging`` seem to be constantly confused by the application engineers that will be consuming this documentation.  Let's just say you want to "add" or _commit_ provenance for a registered object.

How do you commit provenance to the data store?

You can do it one of two ways:

* Conversational
* One action

For the conversational approach, you have to make a call to register the object.  Then, use that UUID in the follow-up call to the ``provenance`` endpoint:

##### Usage

Conversational - using python:

>>> r = requests.post("http://tardis-dev:8000/1.4a/register/KAHN-Test/TT66678/example/description/")
>>> r.text
u'{\n    "UUID": "330480398003867648"\n}'
>>> r.status_code
200
>>> r.json()
{u'UUID': u'330480398003867648'}
>>> my_uuid = r.json()['UUID']
>>> my_uuid
u'330480398003867648'
>>> endpoint = "http://tardis-dev:8000/1.4a/provenance/%s/%s/%s/%s/%s" % (my_uuid,
...                     'lenards', 'Kahn-Data-Commons', 'download', 'dc-view')
>>> r = requests.post(endpoint)
>>> r.status_code
200
>>> r.text
u'{\n    "result": {\n        "Status": "Success", \n        "Details": "Provenance recorded"\n    }\n}'
>>>

Conversational - using cURL:

>  $ curl -X POST "http://tardis-dev:8000/1.4a/provenance/3-Data-Commons/download/dc-view"
>{
>    "result": {
>        "Status": "Success",
>        "Details": "Provenance recorded"
>    }
>}

One action - using Python:



One action - using cURL:
