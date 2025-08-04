import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import base58

import analyzer
from book import Book


@dataclass(frozen=True)
class Node:
    id: str
    desc: str

    def __str__(self) -> str:
        return f"{self.id}: {self.desc}"


@dataclass(frozen=True)
class Relation:
    src: str
    dest: str

    def __str__(self) -> str:
        return f"{self.src} -> {self.dest}"


class Figure:
    def __init__(self, path: str):
        self.root = self._root(path)
        self.nodes = set()
        self.relations = set()

        with ThreadPoolExecutor() as executor:
            results = executor.map(self._process_notebook, self._find_books(path))
            for book_path, ios in results:
                relative_book_path = book_path.replace(self.root, "").lstrip("/")
                book_id = self._generate_id("book", relative_book_path)
                print(book_id, relative_book_path)
                for io in ios:
                    cell_id = f"cell_{io.id}_{book_id}"
                    io_node = Node(id=cell_id, desc=cell_id)
                    self.nodes.add(io_node)
                    for d in io.read:
                        data_id = self._generate_id("data", f"{d}")
                        data_node = Node(id=data_id, desc=f"{d}")
                        self.nodes.add(data_node)
                        rel = Relation(src=data_id, dest=cell_id)
                        self.relations.add(rel)
                    for d in io.write:
                        data_id = self._generate_id("data", f"{d}")
                        data_node = Node(id=data_id, desc=f"{d}")
                        self.nodes.add(data_node)
                        rel = Relation(src=cell_id, dest=data_id)
                        self.relations.add(rel)

    def __str__(self) -> str:
        node_list = "\n".join([f"  {n}" for n in self.nodes])
        relation_list = "\n".join([f"  {r}" for r in self.relations])
        return f"nodes:\n{node_list}\nrelations:\n{relation_list}"

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
