import argparse
import asyncio
import concurrent.futures
import functools
import ssl

from pydantic import ValidationError

from brute_force import brute_force
from shared import (
    CONNECTION_PARSER,
    ConnectionArgs,
    Fail,
    Request,
    Response,
    Success,
    get_and_validate_args,
)


async def echo(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    executor: concurrent.futures.Executor | None = None,
):
    loop = asyncio.get_running_loop()
    found = False
    while not found:
        msg = await reader.read()
        try:
            request = Request.model_validate_json(msg)
        except ValidationError:
            writer.close()
            await writer.wait_closed()
            return
        result = await loop.run_in_executor(
            executor,
            brute_force,
            request.start,
            request.stop,
            request.digest,
            request.charset,
        )
        if result is not None:
            response = Response(state=Success(body=result))
            found = True
        else:
            response = Response(state=Fail())
        try:
            writer.write(response.model_dump_json().encode())
            await writer.drain()
        except ConnectionError:
            print("Client disconnected early.")
            break


async def main():
    parser = argparse.ArgumentParser(parents=[CONNECTION_PARSER])
    args = get_and_validate_args(parser, ConnectionArgs)
    if args.tls:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain("localhost.crt", "localhost.key")
    else:
        ctx = None
    with concurrent.futures.ProcessPoolExecutor() as executor:
        handler = functools.partial(echo, executor=executor)
        async with await asyncio.start_server(
            handler, str(args.host), args.port, ssl=ctx
        ) as server:
            await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
