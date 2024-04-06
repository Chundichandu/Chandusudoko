from pprint import pprint
import pycosat
import sys

def get_board(line):
    board = []
    for i in range(0, 81, 9):
        row_line = line[i:i+9]
        row = [int(char) if char != '.' else 0 for char in row_line]
        board.append(row)
    return board

def get_line(board):
    line_list = []
    for row in board:
        for v in row:
            if v == 0:
                line_list.append('.')
            else:
                line_list.append(str(v))
    return ''.join(line_list)

def run(file_path):
    output = open(file_path.replace('.txt', '_sol.txt'), 'w')
    with open(file_path, 'r') as f:
        for line in f:
            board = get_board(line)
            if solvable(board):
                print('Solvable Writing out')
                output.write(get_line(board))
                output.write('\n')
            else:
                print('Not Solvable')
    output.close()  # Close the output file after writing

def value(i, j, v):
    return i * 100 + j * 10 + v

def is_valid(board):
    # Check rows, columns, and sub-grids for validity
    for i in range(9):
        row = [board[i][j] for j in range(9)]
        if not is_valid_unit(row):
            return False

        column = [board[j][i] for j in range(9)]
        if not is_valid_unit(column):
            return False

    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            square = [board[x][y] for x in range(i, i+3) for y in range(j, j+3)]
            if not is_valid_unit(square):
                return False

    return True

def is_valid_unit(unit):
    seen = set()
    for num in unit:
        if num != 0:
            if num in seen:
                return False
            seen.add(num)
    return True

def solvable(board):
    # Generate clauses for the Sudoku problem
    clauses_list = clauses(board)

    # Use PyCosat to solve the SAT problem
    sol = pycosat.solve(clauses_list)

    # If no solution found or solution invalid, return False
    if sol == 'UNSAT' or sol == 'UNKNOWN':
        return False

    # Extract solution from SAT solution and check validity
    for i in range(1, 10):
        for j in range(1, 10):
            for v in range(1, 10):
                if value(i, j, v) in sol:
                    board[i - 1][j - 1] = v

    return is_valid(board)

def clauses(board):
    clauses_list = []

    # Cell Clauses: At least one of the 9 values for each cell
    for i in range(1, 10):
        for j in range(1, 10):
            clauses_list.append([value(i, j, v) for v in range(1, 10)])

    # Pairwise Exclusion Clauses: No two different values at once for each cell
    for i in range(1, 10):
        for j in range(1, 10):
            for v1 in range(1, 10):
                for v2 in range(v1 + 1, 10):
                    clauses_list.append([-value(i, j, v1), -value(i, j, v2)])

    # Row and Column Clauses: No two cells in the same row or column contain the same digit
    for i in range(1, 10):
        rc_clause([(i, j) for j in range(1, 10)], clauses_list)
        rc_clause([(j, i) for j in range(1, 10)], clauses_list)

    # Square Region (3x3) Clauses: No two cells in the same region contain the same digit
    for i in range(1, 10, 3):
        for j in range(1, 10, 3):
            rc_clause([(i + k % 3, j + k // 3) for k in range(9)], clauses_list)

    # Add known values as unit clauses
    for i in range(1, 10):
        for j in range(1, 10):
            if board[i - 1][j - 1] != 0:
                clauses_list.append([value(i, j, board[i - 1][j - 1])])

    return clauses_list

def rc_clause(cells, clauses_list):
    for i, xi in enumerate(cells):
        for j, xj in enumerate(cells):
            if i < j:
                for v in range(1, 10):
                    clauses_list.append([-value(xi[0], xi[1], v), -value(xj[0], xj[1], v)])

if __name__ == '__main__':
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        run(file_path)
    else:
        file_path = input('Enter the file_path of puzzles: ')
        run(file_path)
