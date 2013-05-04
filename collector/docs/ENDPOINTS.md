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

<pre>
&gt;&gt;&gt; import requests
&gt;&gt;&gt; query = {'service_key': 'KAHN-Test', 'object_id': 'TT:6556-8'}
&gt;&gt;&gt; r = request.get("http://tardis-dev:8000/1.4a/lookup/", params=query)
&gt;&gt;&gt; r = requests.get("http://tardis-dev:8000/1.4a/lookup/", params=query)
&gt;&gt;&gt; r.text
u'{\n    "UUID": "330063643242663936"\n}'
&gt;&gt;&gt;
</pre>

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

<pre>
&gt;&gt;&gt; r = requests.post("http://tardis-dev:8000/1.4a/register/KAHN-Test/TT66678
/example/description/")
&gt;&gt;&gt; r.text
u'{\n    "UU
ID": "330480398003867648"\n}'
&gt;&gt;&gt; r.status_code
200

&gt;&gt;&gt; r.json()
{u'UUID': u'
330480398003867648'}
&gt;&gt;&gt;
</pre>

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

### Parameters

* Conversational:

/provenance/{UUID}/{username}/{service_name}/{event_name}/{category_name}[

* One action:

/provenance/{service_name}/{event_name}/{category_name}

### Optional Parameters

Paremeters not required are:

* proxy_username
* event_data
* version
* track_history
* track_history_code

For the "conversational" calling convention, all optional parameters must be passed as query string arguments

For the "one action" calling convention, these parameters should be included in the post body.

### POST Body Formats

Only JSON and form-urlencoded bodies will be accepted.

The 'Content-Type' header must be set to either:

* 'application/x-www-form-urlencoded'
* 'application/json'

##### Usage

Conversational - using python:

<pre>
&gt;&gt;&gt; r = requests.post("http://tardis-dev:8000/1.4a/register/KAHN-Test/TT66678
/example/description/")
&gt;&gt;&gt; r.text
u'{\n    "UU
ID": "330480398003867648"\n}'
&gt;&gt;&gt; r.status_code
200
&gt;&gt;&gt; r.json()
{u'UUID': u'
330480398003867648'}
&gt;&gt;&gt;
 my_uuid = r.json()['UUID']
&gt;&gt;&gt; my_uuid
u'3304803980
03867648'
&gt;&gt;&gt; endpoint = "http://tardis-dev:8000/1.4a/provenance/%s/%s/%s/%s/%s" % (my_uuid,
...         'lenards', 'Kahn-Data-Commons', 'download', 'dc-view')
&gt;&gt;&gt;
 r = requests.post(endpoint)
&gt;&gt;&gt; r.status_code
200
&gt;&gt;&gt; r.text
u'{\n    "result": {\n        "Status": "Success", \n        "Details": "Provenance recorded"\n
   }\n}'
&gt;&gt;&gt;
</pre>

Conversational - using cURL:

>  $ curl -X POST "http://tardis-dev:8000/1.4a/provenance/3-Data-Commons/download/dc-view"
>{
>    "result": {
>        "Status": "Success",
>        "Details": "Provenance recorded"
>    }
>}


One action - using cURL:

>$ curl -H "Content-Type: application/json" -X POST -d @test_prov_post_case1.json "http://tardis-dev:8000/1.4a/provenance/Kahn-Data-Commons/root-list/dc-view/"
>{
>    "result": {
>        "Status": "Success",
>        "Details": "Provenance recorded"
>    }
>}

This will accept provenance with a POST body.

You can find the data in ``test_prov_post_case1.json`` in the [test-data](https://github.com/iPlantCollaborativeOpenSource/tardis-apis/blob/master/collector/docs/test-data/json/test_prov_post_case1.json) directory.

>$ curl  -H "Content-Type: application/json" -X POST -d @test_prov_post_case2.json "http://tardis-dev:8000/1.4a/provenance/Kahn-Data-Commons/download/dc-view/"
>{
>    "result": {
>        "Status": "Success",
>        "Details": "Provenance recorded"
>    }
>}

This will accept provenance with a POST body - BUT! It is a "one-action" committing of provenence.  See, in the example JSON file, there is no UUID.  But there is enough information for registering an object.  So doing a POST with this will cause the API to register the object, thus relating it to a UUID, then used that UUID to commit provenance on behalf of the calling application for the ``event`` and ``category`` indicated.

You can find the data in ``test_prov_post_case2.json`` in the [test-data](https://github.com/iPlantCollaborativeOpenSource/tardis-apis/blob/master/collector/docs/test-data/json/test_prov_post_case1.json) directory.

Warnings:

If a UUID is present in the POST body and the values for registration (service_key, object_id, object_name, etc) - those values will be ignored and the UUID will be used to commit provenance.

Currently, the positional arguments within the URL of "one action" /provenance POST's is not used for committing provenance.  If those values conflict with the corresponding values within the POST body, it will only affect the logging for the calling application usage of TARDIS Collector.  The point of including them was to allow for load-balancing by calling application, or simple auditing of "implemented" calling convention.  It would be better if these values were using in the committing of provenance and therefore the values within the POST body would be omitted for simplicity (and to remove this silly ``Don't Repeat Yourself`` violation that Andrew Lenards has carelessly introduced.  But he's the author writing this in third person - so it's okay.  He's just scolding himself because that's not how we _should_ be rolling around here.)

## For omissions about the parameters/arguments, review the previous version of the Collector API, v1.2:

[Documentation](https://pods.iplantcollaborative.org/wiki/display/csmgmt/vC.1.2)

## NOTE

Collector API v1.4 is *not* backward compatible with previous versions.
