import json

from shared import Request, Response


def main():
    with open(
        "schemas/request.schema.json", mode="w+", encoding="utf-8"
    ) as req_file, open(
        "schemas/response.schema.json", mode="w+", encoding="utf-8"
    ) as rsp_file:
        json.dump(Request.model_json_schema(), req_file, indent=2)
        json.dump(Response.model_json_schema(), rsp_file, indent=2)


if __name__ == "__main__":
    main()
