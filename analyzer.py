import json
import os
from dataclasses import dataclass

from openai import OpenAI

models = [
    {
        "env": "NOTEMAP_DEEPSEEK",
        "url": "https://api.deepseek.com",
        "mod": "deepseek-chat",
    },
    {
        "env": "NOTEMAP_KIMI_K2",
        "url": "https://api.moonshot.cn/v1",
        "mod": "kimi-k2-0711-preview",
    },
    {
        "env": "NOTEMAP_OPENROUTER_DEEPSEEK_CHAT_V3_0324_FREE",
        "url": "https://openrouter.ai/api/v1",
        "mod": "deepseek/deepseek-chat-v3-0324:free",
    },
    {
        "env": "NOTEMAP_OPENROUTER_KIMI_K2_FREE",
        "url": "https://openrouter.ai/api/v1",
        "mod": "moonshotai/kimi-k2:free",
    },
    {
        "env": "NOTEMAP_OPENROUTER_QWEN3_235B_A22B_FREE",
        "url": "https://openrouter.ai/api/v1",
        "mod": "qwen/qwen3-235b-a22b:free",
    },
]

prompt = """
I will give you some code snippets, then you tell me each snippet read data from where, and write data to where, if they do read or write.

your answer should be formatted in json like this:

```
{
"rw": [
    {
    "id": "kfgj8789",
    "read": [{"kind": "table", "location": "db", "name": "abc"}],
    "write": [{"kind": "file", "location": "/dir", "name": "xyz"}]
    }
]
}
```

`kind` can be table, view, file

if `kind` is table or view, it must be in a database, fill the location of database into `location`, that location can be a db in memory

if `kind` is file, fill the name of dir containing that file into `location`

here are the snippets:
"""


@dataclass(frozen=True)
class Data:
    kind: str
    location: str
    name: str

    def __str__(self) -> str:
        return f"{self.kind}:{self.location}:{self.name}"


@dataclass(frozen=True)
class IO:
    id: str
    read: set[Data]
    write: set[Data]

    def read_list(self) -> list[Data]:
        return sorted(list(self.read), key=str)

    def write_list(self) -> list[Data]:
        return sorted(list(self.write), key=str)


def parse(snippets: str) -> list[IO]:
    result = request(snippets)
    return [
        IO(
            id=res["id"],
            read={Data(**r) for r in res.get("read", [])},
            write={Data(**r) for r in res.get("write", [])},
        )
        for res in json.loads(result).get("rw", [])
    ]


def request(snippets: str) -> str:
    config = _get_model_config()
    api_key = os.getenv(config["env"])
    base_url = config["url"]
    model = config["mod"]

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"{prompt}\n\n{snippets}"}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _get_model_config() -> dict[str, str]:
    for model in models:
        if os.getenv(model["env"]):
            return model
    return models[0]
