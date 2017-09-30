assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

# Global variables
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
cols_rev = cols[::-1]
dx = [[rows[i]+cols[i] for i in range(len(rows))]]
dy= [[rows[i]+cols_rev[i] for i in range(len(rows))]]

# Diagonal sudoku
diagonal_sudoku = 1 
if diagonal_sudoku == 1:
    unitlist = row_units + column_units + square_units + dx + dy
else:
    unitlist = row_units + column_units + square_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)