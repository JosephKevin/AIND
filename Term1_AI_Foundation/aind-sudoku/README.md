# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: Naked twins problem is when we have 2 boxes of a unit have possibility of having the same 2 numbers. 

For example 'A1': 23, 'A6': 32 are naked twins.
In this example we can have 2 situations 'A1': 2 and 'A6': 3 or 'A1': 3 and 'A6': 2, which implies that none of common peers of 'A1' and 'A6' can have the numbers 2 or 3. That is none of these boxes 'A2','A3','A4','A5','A7','A8','A9' can have a value of 2 or 3. 

This is our constraint. We repeated this for all units (row, column and square units (if diagonal sudoku we consider diagonal units also)). Once the constraint has been applied across all units we will have solved the Naked twins problem.

In this problem we apply the concept of constraint propagations. We identify the constraint (no common peers of the naked twins can have the digits occuring in the naked twin boxes) and then we propagate it across the units. This is how we apply constraint propagation to solve naked twins problem.


# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: In order to solve the diagonal sudoku problem, we must think of the two diagonals as an additional unit. Now in addition to row, column and square units we have 2 diagonal units.
	
Our constraint for the diagonal units will be the same as out constraints for other units(the single digit number can occur only once among the units). When we propagate this constraint over all units we will have solved for a diagonal sudoku.

In this problem we apply constraint propagations. we already have constraints for units that were being satisfied. Since a diagonal unit will have the same constraint as any previous unit all we had to do was add the diagonal units to our existing units list and then propagate through the units. This is how we solve a diagonal sudoku.	

### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solution.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Submission
Before submitting your solution to a reviewer, you are required to submit your project to Udacity's Project Assistant, which will provide some initial feedback.  

The setup is simple.  If you have not installed the client tool already, then you may do so with the command `pip install udacity-pa`.  

To submit your code to the project assistant, run `udacity submit` from within the top-level directory of this project.  You will be prompted for a username and password.  If you login using google or facebook, visit [this link](https://project-assistant.udacity.com/auth_tokens/jwt_login for alternate login instructions.

This process will create a zipfile in your top-level directory named sudoku-<id>.zip.  This is the file that you should submit to the Udacity reviews system.

