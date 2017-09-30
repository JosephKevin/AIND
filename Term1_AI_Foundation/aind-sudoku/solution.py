import sys
import itertools
import logging
from functools import reduce
import re
from utils import *
logging.basicConfig(filename='./logs/sudoku.log',level=logging.ERROR)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def check_if_sudoku_dict(values):
    """
    Function to check if a given input is a sudoku, of the form {'A1': 123, 'A2': 1,...'I9': 9}

    Args:
       values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        is_sudoku: boolean denoting if the given input dictionary is of a valid sudoku form. 
    """
    if len(values) == 81 and list(values.keys()) == boxes:
        return True
    else:
        return False

def find_twins(values):
    """
    Find Naked twins
    STEPS:
        1. Loop through the possible twins list.
        2. For each possible twin look at all its peers.
        3. If any of the possible twins peer's value matches the possible twin's value then we have a naked twins pair. 
        4. We are saving the naked twin pair as a list of lists [[pair1], [pair2], ..] but as one might expect we
           will get duplicates eg) [[A1, F1], [A1, B2],...., [F1,A1]]. 
           In order to prevent this we sort each individual pair list before appending it to the naked_twins lists i.e.
           now we will have [[A1, F1], [A1, B2],....,[A1, F1] ].
        5. We remove duplicates in a list of list using itertools to get the unique list of naked twin pairs. 

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        Naked_twins: a list of lists containing all the naked twins.
    """
    possible_twins = [box for box in values if len(values[box]) == 2]    
    naked_twins = []
    for possible_twin in possible_twins: 
        for peer in peers[possible_twin]: 
            if values[peer] == values[possible_twin]: 
                naked_twins_pair = [possible_twin, peer]
                naked_twins_pair.sort() 
                naked_twins.append(naked_twins_pair)
    naked_twins.sort()
    naked_twins = list(k for k,_ in itertools.groupby(naked_twins)) 
    return naked_twins

def eliminate_twins(values, naked_twins, twin_size=2):
    """
    Remove naked pair value from its peerss
    STEPS:
        1. For each pair of naked_twins, get the common peers. eg naked_twin = ['A1', 'A2']
            then their peers = ['A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
        2. Remove the value contained in the naked_twins from its common peers.
        3. return values

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        Naked_twins: a list of lists containing all the naked twins.
        twin_size: the size of the twin pairs. (default 2)

    Returns:
        values(dict): a dictionary of the form {'box_name': '123456789', ...} with the naked_twins removed
    """
    for naked_twin in naked_twins:
        naked_peers = reduce(lambda x,y: peers[x] & peers[y], naked_twin) - set(naked_twin) 
        for box in naked_peers:
            if len(values[box]) >= twin_size: 
                for rm_nbr in values[naked_twin[0]]: 
                    values = assign_value(values, box, values[box].replace(rm_nbr, '')) 
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    try:
        naked_twins = find_twins(values)
        values = eliminate_twins(values, naked_twins)
        return values
    except:
        logging.error('Error in naked_twins method', exc_info=True)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
   
    Args:
        grid(string) - A grid in string form.
   
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    gv = dict(zip(boxes, grid))
    all_digits = '123456789'
    for key in gv:
        if (gv[key] == '.'):
            gv[key] = all_digits
    return gv
    

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    """
    Function to look at solved boxes and remove that value from other possibilities in it peers.

    Args:
        values: the sudoku in {key:value} format {box: value_in_box}

    Returns:
        values: the sudoku with all the possible repetition of solved box among its peers removed.
    """
    assert check_if_sudoku_dict(values), 'Not a valid sudoku input in eliminate function'
    solved_box = [box for box in values if len(values[box]) == 1]
    for box in solved_box:
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(values[box], ''))
    return values  

def only_choice(values):
    """
    Function to enforce the constraint that every unit must only have one occurrence of every number.

    params:
        values: the sudoku in {key:value} format {box: value_in_box}

    Returns:
        values: the only choice conditions removed
    """
    assert check_if_sudoku_dict(values), 'Not a valid sudoku input in only_choice function'
    for unit in unitlist:
        for digit in '123456789':
            v = [box for box in unit if digit in values[box]]
            if len(v) == 1:
                values = assign_value(values, v[0], digit)
    return values

def reduce_puzzle(values):
    """
    Function to applytthe constraint repeatedly

    This function uses 3 constraints 
    1. eliminate
    2. only choice
    3. naked twins
    We perform these constrainst iteratively until there is no improvement in the number of boxes solved.

    Args:
        values: the sudoku in {key:value} format {box: value_in_box}

    Returns:
        values: the solved sudoku, 
            if unable to solve it returns false
    """
    assert check_if_sudoku_dict(values), 'Not a valid sudoku input in reduce_puzzle function'
    stalled = False
    while not stalled:
        initial_no_of_solved = len([box for box in values if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        final_no_of_solved = len([box for box in values if len(values[box]) == 1])
        if (initial_no_of_solved == final_no_of_solved):
            stalled = True
        if (len([box for box in values.keys() if len(values[box]) == 0])):
            return False
    return values

def search(values):
    """
    Function to do constraint propagation and search

    STEPS:
    1. Try to solve sudoku using constraint propagation methods

        If constraint propagation doesnt give complete results    
    2. Do a search for all possible solutions
        2.1 Choose a value to split
        2.2 split on the unsolved_box
        2.3 iteratively solve 

    Args:
        values: the sudoku in {key:value} format {box: value_in_box}

    Returns:
        values: the solved sudoku
    """
    logging.info('Search method has started')
    assert check_if_sudoku_dict(values), 'Not a valid sudoku input in search function'
    values = reduce_puzzle(values)
    if values is False:
        return False
    elif all(len(values[box]) == 1 for box in boxes):
        return values
    try:

        min_len, unsolved_box = min([(len(values[box]),box) for box in values if len(values[box]) > 1 ])
        
        for value in values[unsolved_box]:
            new_sdk = values.copy()
            new_sdk[unsolved_box] = value
            attempt = search(new_sdk)
            if attempt:
                return attempt
        logging.info('Search method has been successful')
    except:
        logging.error('Error in search method', exc_info=True)

def solve(grid):
    """
    Find the solution to a Sudoku grid.

        1. Convert the string representation of sudoku to a dictionary of {box: value,...} pairs.
        2. Call the function that does, constraint propagartion and search to get the result.
    
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    assert not bool(re.search('[a-zA-Z]', grid)), 'Please check the input, grid has an alphabet: %s' % grid
    logging.info('Creating a sudoku from %s'%(grid))
    values = grid_values(grid)
    logging.info('Starting to solve the sudoku')
    values = search(values)
    if values is False:
        logging.info('The sudoku could not be solved')
    else:
        logging.info('The sudoku has been solved')
    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid)) 
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
