import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import base58

import analyzer
from book import Book


@dataclass(frozen=True)
class Note:
    book_id: str
    path: str
    cell_ids: list[str]


@dataclass(frozen=True)
class Cell:
    id: str
    desc: str


@dataclass(frozen=True)
class Data:
    id: str
    desc: str


@dataclass(frozen=True)
class Relation:
    src: str
    dest: str

    def __str__(self) -> str:
        return f"{self.src} -> {self.dest}"


class Figure:
    def __init__(self, path: str):
        self.root = self._root(path)

        self.notes = []
        self.cells = {}
        self.datas = {}
        self.rws = set()

        with ThreadPoolExecutor() as executor:
            results = executor.map(self._process_notebook, self._find_books(path))
            for book_path, ios in results:
                relative_book_path = book_path.replace(self.root, "").lstrip("/")
                book_id = self._generate_id("book", relative_book_path)
                cell_ids = []
                for io in ios:
                    cell_id = f"cell_{io.id}_{book_id}"
                    cell_ids.append(cell_id)
                    self.cells[cell_id] = Cell(id=cell_id, desc=cell_id)
                    for d in io.read:
                        data_id = self._generate_id("data", f"{d}")
                        self.datas[data_id] = Data(id=data_id, desc=f"{d}")
                        self.rws.add(Relation(src=data_id, dest=cell_id))
                    for d in io.write:
                        data_id = self._generate_id("data", f"{d}")
                        self.datas[data_id] = Data(id=data_id, desc=f"{d}")
                        self.rws.add(Relation(src=cell_id, dest=data_id))
                self.notes.append(
                    Note(book_id=book_id, path=relative_book_path, cell_ids=cell_ids)
                )

    def __str__(self) -> str:
        return graphviz(self)

    def _process_notebook(self, path) -> tuple[str, list[analyzer.IO]]:
        book = Book(path)
        snippets = book.code_snippets()
        in_out = analyzer.parse(snippets)
        return (book.full_path, in_out)

    def _root(self, path) -> str:
        path = Path(path).resolve()
        if path.is_file():
            return str(path.parent)
        return str(path)

    def _find_books(self, path):
        path = Path(path)
        if path.is_file() and path.suffix == ".ipynb":
            yield str(path)
        elif path.is_dir():
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".ipynb"):
                        notebook_path = os.path.join(root, file)
                        yield notebook_path

    def _generate_id(self, prefix: str, s: str) -> str:
        bytes = s.encode("utf-8")
        encoded_bytes = base58.b58encode(bytes)
        return f"{prefix}_{encoded_bytes.decode('ascii')}"


def graphviz(f: Figure) -> str:
    newline = "\n  "

    def subgraph(n: Note) -> str:
        seq = "->".join([cid for cid in n.cell_ids])
        return f"subgraph cluster_{n.book_id}{{ {seq} }}"

    def desc(d: Data) -> str:
        return f'{d.id}[label="{d.desc}"]'

    descs = newline.join(["// description"] + [desc(d) for _, d in f.datas.items()])
    notes = newline.join(["// notes"] + [subgraph(n) for n in f.notes])
    rels = newline.join(["// relations"] + [f"{rw.src} -> {rw.dest}" for rw in f.rws])

    return f"digraph G {{{newline}node[shape=Square]{newline}{descs}{newline}{notes}{newline}{rels}\n}}"
