Problem:

I need a way to automate creating proxy definitions for EZproxy. When the
library adds or modifies a database, they have to let me know. After that, I
check the database configurations for the proxy URL, and the groups that have
access to this database. For each group that has access to this database, I
have to check whether the starting point URL located in the admin page will be
proxied for that host. I do this by searching through all the database
configurations for the EZproxy "group" for a stanza that matches the hostname
of the URL defined in the library database page.  I also check whether a
database stanza for this vendor is available on OCLC's support website for
EZproxy. If the hostname matches, and I am able to get to the site through
EZproxy, then it should be good to go. If I need to add or modify a stanza,
then I modify the stanza, then restart EZproxy.

So if I were to automate this, I would need to expose the following functions
in an API:
- When a library database configuration is changed, notify the proxy (or proxy
  administrator)
- A controller to send requests to specific instances of the API
 - Translation from starting point URL to origin (complete)
 - Search proxy instance for existing stanza with hostname (or starting point
  URL with above translation embedded) (complete)
  # - Requires parsing database stanza files (complete)
- Check OCLC site for stanza using fuzzy matching on title? (optional)
  - Requires parsing HTML for item list.
- Create stanza with options identified
  - Include logic to make sure that at least Title and URL are included.
- Restart ezproxy

Other functions that may be useful in the future:
- query tasks by matching URL/Hostname directive, retrieve more details with
  stanza ID
- start and stop ezproxy
- Delete or modify database stanzas
- Test if user can authenticate to database
- Modify GLOBAL stanza

Deployment requirements:
- HTTP Rest service
- If it can be deployed in a container, all the better


Implementation Ideas:
- System API
  - Attaches to specific EZproxy instance
- Process API
  - separate layer to serve requests to different instances of proxy

- Use python/flask libraries to create API
  - If written for python 2.7, does not require extra software downloads
  - Been around longer than Node.JS
  - Node.JS is picking up speed though. It may be more maintainable in the future?

Considerations:
- make stanza parsing robust enough so that if someone manually edits the file,
  the API will still be useable.
  - otherwise make a note at the top not to edit the file unless they
    understand the API expected syntax.

