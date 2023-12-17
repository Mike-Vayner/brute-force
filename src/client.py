import argparse
import asyncio
import ssl
import string
import sys

from pydantic import ValidationError

from shared import (
    CONNECTION_PARSER,
    ConnectionArgs,
    Request,
    Response,
    get_and_validate_args,
    str_increment,
)


class Args(Request, ConnectionArgs):
    pass


async def main():
    parser = argparse.ArgumentParser(
        parents=[CONNECTION_PARSER], conflict_handler="resolve"
    )
    parser.add_argument("start")
    parser.add_argument("stop")
    parser.add_argument("digest")
    parser.add_argument("--charset", default=string.ascii_lowercase)
    parser.add_argument("--host", default="::1")
    args = get_and_validate_args(parser, Args)
    if args.tls:
        ctx = ssl.create_default_context()
    else:
        ctx = None
    reader, writer = await asyncio.open_connection(str(args.host), args.port, ssl=ctx)
    try:
        print(f"Connected to {writer.transport.get_extra_info("peername")}")
        start = args.start
        stop = ""
        while len(stop) <= len(args.stop):
            stop = str_increment(start[:-4]) + start[-4:]
            if len(stop) == len(args.stop):
                stop = min(stop, args.stop)
            request = Request(
                start=start, stop=stop, digest=args.digest, charset=args.charset
            )
            print(f"Requesting in range {start} - {stop}")
            writer.write(request.model_dump_json().encode())
            await writer.drain()
            response_json = await reader.read()
            try:
                response = Response.model_validate_json(response_json)
            except ValidationError as err:
                print(err)
                sys.exit(1)
            state = response.state
            if state.status == 200:
                print(f"The password is {state.body}")
                break
            print("Failed in this range")
            if stop == args.stop:
                print("The password could not be determined")
                break
            start = str_increment(stop, args.charset)
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Cancelled early")
