import os
import json
from dataclasses import dataclass
from openai import OpenAI
from typing import List

prompt = """
I will give you some code snippets, then you tell me each snippet read data from where, and write data to where, if they do read or write.

your answer should be formatted in json like this:

```
{
"rw": [
    {
    "id": "kfgj8789",
    "read": [{"kind": "table", "name": "abc"}],
    "write": [{"kind": "file", "name": "xyz"}]
    }
]
}
```

kind can be table, view, file

here are the snippets:
"""


@dataclass
class Data:
    kind: str
    name: str


@dataclass
class IO:
    id: str
    read: List[Data]
    write: List[Data]


def parse(snippets: str) -> List[IO]:
    result = request(snippets)
    return [
        IO(
            id=res["id"],
            read=[Data(kind=r["kind"], name=r["name"]) for r in res.get("read", [])],
            write=[Data(kind=r["kind"], name=r["name"]) for r in res.get("write", [])],
        )
        for res in json.loads(result).get("rw", [])
    ]


def request(snippets: str) -> str:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.deepseek.com"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": f"{prompt}\n\n{snippets}"}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content
