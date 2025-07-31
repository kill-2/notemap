import json
from dataclasses import dataclass


@dataclass
class Cell:
    cell_type: str
    id: str
    source: str
    lang: str = None

    @property
    def kind(self) -> str:
        if self.cell_type == "markdown":
            return "md"
        if self.cell_type == "code":
            if self.source.startswith("%%"):
                return self.source[2 : self.source.find("\n")]
            return self.lang if self.lang is not None else "python"
        return self.cell_type

    @property
    def source_no_magic(self) -> str:
        if self.source.startswith("%%"):
            return self.source[self.source.find("\n") + 1 :]
        return self.source

    @property
    def src(self) -> str:
        s = self.source_no_magic.replace("\n", "\\n")
        return s[:47] + "..." if len(s) > 50 else s


class Book:
    def __init__(self, file_path: str):
        self.cells = self._read(file_path)

    def code_snippets(self) -> str:
        output = ""
        for cell in self.cells:
            if cell.cell_type == "code":
                output += f"code snippet {cell.id}:\n\n"
                output += f"```{cell.kind}\n{cell.source_no_magic}\n```\n\n"
        return output

    def _read(self, file_path: str) -> list[Cell]:
        cells = []
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
            for cell_data in notebook["cells"]:
                source = "".join(cell_data["source"])
                lang = (
                    cell_data.get("metadata", {})
                    .get("vscode", {})
                    .get("languageId", None)
                )
                cell = Cell(
                    cell_type=cell_data["cell_type"],
                    id=cell_data["id"],
                    source=source,
                    lang=lang,
                )
                cells.append(cell)
        return cells
