import inspect
import json
from typing import get_type_hints
import docstring_parser

def function_to_openapi(func):
    docstring = docstring_parser.parse(func.__doc__)
    signature = inspect.signature(func)
    parameters = signature.parameters
    type_hints = get_type_hints(func)

    openapi_json = {
        "name": func.__name__,
        "description": docstring.short_description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    for param in parameters.values():
        param_type = type_hints.get(param.name, 'any').__name__.lower()
        param_description = next(
            (p.description for p in docstring.params if p.arg_name == param.name), "")
        openapi_json["parameters"]["properties"][param.name] = {
            "type": param_type,
            "description": param_description
        }
        openapi_json["parameters"]["required"].append(param.name)

    return openapi_json


# Convert the function to OpenAPI JSON
#openapi_json = function_to_openapi(addTwo)
#print(json.dumps(openapi_json, indent=4))
