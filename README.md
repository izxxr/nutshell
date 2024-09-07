# nutshell
[Nutshell](https://izxxr.medium.com/writing-a-pocket-sized-url-shortener-in-python-a1f9ab64b14a) (as the name implies) is a
pocket-sized, simple link shortener written in Python using Quart.

This is a personal link shortener that was written within the span of two hours and provides the
following features:

- Random, concise and support for custom URLs
- Password protected URLs
- Temporary link deactivation
- URL metrics (total visits, successful visits, last visit etc.)
- API interface for CRUD operations on links
- Internal LRU cache to regulate database transactions

## Installation
_Python 3.8 or higher is required._

Clone this repository and install the dependencies:

```
$ git clone https://github.com/izxxr/nutshell
$ cd nutshell
$ pip install -r requirements.txt
```

Create an `.env` file and define a `NUTSHELL_AUTH_TOKEN` environment variable. This variable
stores the authentication token that will be sent to API to create, read, update and delete
URLs. Make sure to use a strong combination of characters. It has to be greater than 10 characters.

`.env` file:

```
NUTSHELL_AUTH_TOKEN="..."
```

Other optional variables to control the application behaviour are:

- `NUTSHELL_CACHE_LIMIT`: The number of links cached in memory at a time. Upon exceeding this numbers,
  least recently used links are evicted from cache. Default value is 50.

Run the application on local development server:

```
$ quart run
```

Use the following options in run command to manipulate various server options:

- `-h` or `--host`: The host to bind to.
- `-p` or `--port`: The port number to bind to.
- `--reload`/`--no-reload`: Whether to enable or disable reloader (disabled by default).

## Link Object
On the heart of nutshell is the **link** object that represents a shortened URL. Following
fields are part of the link object:

- `code`: The unique link code.
- `url`: The URL that the link redirects to. (only HTTP/HTTPs URLs allowed)
- `password`: The password to access this link, if any, otherwise null.
- `created_at`: The time, in ISO format, when the link was created.
- `last_visited`: The time, in ISO format, when the link was last visited.
- `active`: Whether the link is active and redirecting. If false, the link is temporarily disabled.
- `raw_visit_count`: The number of times link was accessed.
- `visit_count`: The number of times link was accessed *successfully*.

`visit_count` and `raw_visit_count` are same for unauthorized links. For password protected links, `raw_visit_count`
indicates the number of times the link was accessed regardless of whether password was entered correctly or not and
`visit_count` indicates the number of times password was entered correctly.

## CRUD operations
The following routes are used for managing links.

All sub-routes in `/links` require authorization using bearer token in the `Authorization`
header. The value for this header should use `Bearer` scheme followed by the authorization token
that was set in .env file during installation. E.g. `Bearer ABCDEFGHIJKL123456789`

If this header is omitted, `401: Unauthorized` is returned. If the authorization token is invalid,
`403: Forbidden` is returned. `404: Not Found` and `400: Bad Request` are returned, respectively, when
a link does not exist and when given request data is invalid.

### POST `/links` - Create a link
Creates a link.

The following parameters are to be passed in JSON body:

- `url` (required): the URL that shortened link points to.
- `code`: The custom code for this link. If not provided, a random six digits code is generated.
- `active`: Whether the link is created as active.
- `password`: The password to access this link, if any.

`code` cannot be changed once created. If `code` is taken, `409: Conflict` is returned.

Returns the created link object.

### GET `/links` - Get All Links
Returns the list of link objects representing all created links.

### GET `/links/<code>` - Get Link
Returns the link object corresponding to the given `code`.

### PATCH `/links/<code>` - Update Link
Updates a link.

The following parameters are to be passed in JSON body:

- `url`: the URL that shortened link points to.
- `active`: Whether the link is active.
- `password`: The password to access this link, if any. Set null to remove password.

Returns the updated link object.

### DELETE `/links/<code>` - Delete Link
Deletes a link.

Returns `204: No Content` on successful deletion.

## Accessing links
The links can be accessed by using the shortened URL code on index. For example, if Nutshell is
hosted on localhost at port 5000, the link `ABCDEF` can be accessed by accessing http://localhost:5000/ABCDEF

If a URL is password protected, the user will be required to enter a password before being able
to redirect to the target URL.

## License and Contributions
Any pull requests and issues, small or large, are welcome. For license information, see `LICENSE` file.
