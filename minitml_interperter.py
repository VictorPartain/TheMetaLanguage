import re

variables = {}


def eval_line(line):
    line = line.strip()

    # PRINT STRING
    if line.startswith("print "):
        value = line[6:].strip()

        if value.startswith('"'):
            print(value.strip('"'))
        else:
            print(variables.get(value, f"Undefined variable: {value}"))

    # VARIABLE
    elif line.startswith("let "):
        match = re.match(r'let (\w+) = (.+)', line)
        name, val = match.groups()

        if val.startswith('"'):
            variables[name] = val.strip('"')
        else:
            variables[name] = int(val)

    # FIZZBUZZ
    elif line.startswith("fizzbuzz"):
        _, start, end = line.split()
        start, end = int(start), int(end)

        for i in range(start, end + 1):
            if i % 15 == 0:
                print("FizzBuzz")
            elif i % 3 == 0:
                print("Fizz")
            elif i % 5 == 0:
                print("Buzz")
            else:
                print(i)


def run_block(lines, start_index):
    i = start_index

    while i < len(lines):
        line = lines[i].strip()

        if line == "}":
            return i

        if line.startswith("repeat"):
            count = int(line.split()[1])

            block_start = i + 1
            block_end = run_block(lines, block_start)

            for _ in range(count):
                run_block(lines, block_start)

            i = block_end

        else:
            eval_line(line)

        i += 1

    return i


def run_file(filename):
    with open(filename) as f:
        lines = f.readlines()

    run_block(lines, 0)


if __name__ == "__main__":
    run_file("hello_world.mtml")
    run_file("fizzbuzz.mtml")
    run_file("variables.mtml")
    run_file("counting.mtml")
    run_file("complex.mtml")