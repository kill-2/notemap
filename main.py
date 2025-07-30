import argparse
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
        if self.cell_type == 'markdown':
            return 'md'
        if self.cell_type == 'code':
            if self.source.startswith('%%'):
                return self.source[2:self.source.find('\n')]
            return self.lang if self.lang is not None else 'py'
        return self.cell_type

    @property
    def source_no_magic(self) -> str:
        if self.source.startswith('%%'):
            return self.source[self.source.find('\n') + 1:]
        return self.source

    @property
    def src(self) -> str:
        s = self.source_no_magic.replace('\n', '\\n')
        return s[:47] + '...' if len(s) > 50 else s


def read_notebook(file_path: str) -> list[Cell]:
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = []
    for cell_data in notebook['cells']:
        source = ''.join(cell_data['source'])
        lang = cell_data.get('metadata', {}).get('vscode', {}).get('languageId', None)
        cell = Cell(
            cell_type=cell_data['cell_type'],
            id=cell_data['id'],
            source=source,
            lang=lang
        )
        cells.append(cell)
    return cells


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('notebook', help='Path to .ipynb notebook file')
    args = parser.parse_args()
    
    cells = read_notebook(args.notebook)
    for cell in cells:
        print(f"Cell {cell.id} ({cell.kind}): {cell.src}")


if __name__ == "__main__":
    main()
