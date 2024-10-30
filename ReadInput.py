def read_input_file(filename):
    with open(filename, 'r') as file:
        first_line = file.readline().strip()
        numbers = list(map(int, first_line.split()))

        grid = []
        for line in file:
            grid.append(list(line.strip()))

        max_length = max(len(row) for row in grid)

        for row in grid:
            row.extend([' '] * (max_length - len(row)))

    return numbers, grid