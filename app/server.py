import gspread
import time
from flask import Flask
from memo import memoize_with_expiry
import random

app = Flask(__name__)
gc = gspread.service_account(filename='./credentials.json')

@memoize_with_expiry(5)
def get_all_cells():
    sh = gc.open("Random Generator")
    cells = sh.sheet1.get_all_values()
    return cells

class Column:
    @staticmethod
    def parse_item(raw_item):
        # TODO allow weighting
        return (raw_item, 1)

    def __init__(self, items):
        self.items = dict(Column.parse_item(i) for i in items)
        self.total_weight = sum(self.items.values())

    def sample(self):
        scalar = random.randrange(0, self.total_weight)
        for item, weight in self.items.items():
            scalar -= weight
            if scalar < 0:
                return item
        return None

def all_as_columns():
    all_cells = get_all_cells()
    # Have as many columns as length of first row
    # We could do some clever zipping, but its not really necessary
    columns = []
    for col_index in range(len(all_cells[0])):
        column_items = [row[col_index] for row in all_cells]
        column_items = [c for c in column_items if c]
        columns.append(Column(column_items))
        print("TEST")
    return columns

@app.route('/')
def hello():
    cols = all_as_columns()
    return " ".join(c.sample() for c in cols)
