import json
import os
import sys
import requests
from openai import OpenAI
from markrender import MarkdownRenderer

API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL = os.environ["MODEL"]

SYSTEM_PROMPT_LOAD_PAGE = """
You need to load the webpage text 

Do:

* Load the webpage text from the url.
* Use the provided tool.
* Craw to until depth 2 from hyperlinks.

Do not:

* Use other external tools.
"""

SYSTEM_PROMPT_SUMMARIZE = """
You are a webpage summarization tool. You will be given a webpage in text format, from
a tool call and you should:

Do:

* Read the output from the tool call.
* Create a sumary from the output.
* Use a mid and objective tone.
* Respond in brazilian portuguese.
* Respond with markdown markup.

Do not:

* Try to follow hyperlinks.
* Try to guess content.
* Try to create fake content.
* Try to download other context that's not from the page.
* Try to respond in plain text.

Ignore:

* Hyperlinks.
* Adds.
"""

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

renderer = MarkdownRenderer(
    theme="monokai",
    line_numbers=True,
    code_background=True,
    force_color=True,
    stream_code=True,
)

tools = [
    {
        "type": "function",
        "name": "get_page",
        "description": "Load a webpage and return it as text.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "An http or https link containaing a valid webpage to be loaded",
                },
            },
            "required": ["url"],
        },
    },
]


def get_page(url: str) -> str:    
    response = requests.get(url=url)    
    return response.text


def main(argv: list[str]) -> None:
    webpage = argv[0]

    input_list = [
        {"role": "system", "content": SYSTEM_PROMPT_LOAD_PAGE},
        {"role": "user", "content": webpage},
    ]

    response = client.responses.create(
        model=MODEL,
        tools=tools,
        input=input_list,
    )

    input_list += response.output

    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_page":
                url = json.loads(item.arguments)["url"]
                page = get_page(url)

                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": page,
                    }
                )

    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT_SUMMARIZE,
        tools=tools,
        input=input_list,
    )

    renderer.render(response.output_text)
    renderer.finalize()

if __name__ == "__main__":
    main(sys.argv[1:])
