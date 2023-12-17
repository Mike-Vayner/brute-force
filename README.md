# User Guide

## The Server

The server operates by default on port 7200, though this can be changed with the `--port` option.

## The Client

The client must get its arguments from the command line, and preferably change the target connection with the `--host` option.

# Protocol

Detailed schema definitions are located in the [schemas](/schemas) directory.

After connection, the client sends Requests in the form of
```
{
  start: str,
  stop: str,
  digest: str,
  charset: str
}
```
to which the server will respond with either a Success state or a Fail state in the form of
```
{
  state: {
    status: 200,
    body: str
  } or { status: 404 }
}