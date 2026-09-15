import os
import sys
from openai import OpenAI
from markrender import MarkdownRenderer

API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]

SYSTEM_PROMPT = """
You are a webpage summarization tool. You will be given a url to an webpage and you should:

* Load the webpage from the link.
* Read it's content.
* Create a sumary from the content.
* Use a mid and objective tone.
* Answer with markdown markup.
* Answer in brazilian portuguese.

Ignore:

* Hyperlinks.
* Adds.

Do not:

* Follow hyperlinks.
* Guess content.
* Create fake content.
* Download content that's not the page content.
"""

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

renderer = MarkdownRenderer(
    theme="github-dark",
    line_numbers=True,
    code_background=True,
    force_color=True,
    stream_code=True,
)

def main(argv: list[str]) -> None:

    webpage = argv[0]

    response = client.chat.completions.create(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": webpage},
        ],
    )

    renderer.render(response.choices[0].message.content)
    renderer.finalize()    


if __name__ == "__main__":
    main(sys.argv[1:])
