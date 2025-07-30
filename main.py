import argparse
import json
from dataclasses import dataclass


@dataclass
class Cell:
    cell_type: str
    id: str
    source: str


def read_notebook(file_path: str) -> list[Cell]:
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = []
    for cell_data in notebook['cells']:
        source = ''.join(cell_data['source'])
        cell = Cell(
            cell_type=cell_data['cell_type'],
            id=cell_data['id'],
            source=source
        )
        cells.append(cell)
    return cells


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('notebook', help='Path to .ipynb notebook file')
    args = parser.parse_args()
    
    cells = read_notebook(args.notebook)
    for cell in cells:
        print(f"Cell {cell.id} ({cell.cell_type}): {cell.source[:50]}...")


if __name__ == "__main__":
    main()
