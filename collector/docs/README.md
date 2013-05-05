
# TARDIS Collector

Quick notes on the alpha release:

* the object registration endpoint now requires a "service_key" in addition to the correlation identifier from the calling service (this "correlation identifier" is the object id within the calling service's domain). The "key" is like a "Confluence Space" key or the short "text" key that JIRA uses. It is a short, 10-character, alpha-numeric (plus underscores & dashes) sequence that is used when calling into the API. It provides a "scoping" of the {{object id}}s to the service that is calling (which avoid unintended collisions or conflicts between services' objects).

* the provenance endpoint can be called with an HTTP POST body that is "form url-encoded" or JSON.

* the provenance endpoint can also be HTTP POST'd to without registering an object if and only if the information for registering the object is included in the body of the post request.

For a more detailed view of the endpoints, please go to the [ENDPOINTS.md](https://github.com/iPlantCollaborativeOpenSource/tardis-apis/blob/master/collector/docs/ENDPOINTS.md)

## TARDIS Collector Schema

The schema for the latest version (v1.4) has been reworked and will require
anyone deploying to drop their tables.  See the current schema [here](https://github.com/iPlantCollaborativeOpenSource/tardis-apis/blob/master/collector/sql/current_schema.sql).

You can still add a minimal data set for exploring and playing with the API
[here](https://github.com/iPlantCollaborativeOpenSource/tardis-apis/blob/master/collector/sql/data/add_minimal_data.sql).
