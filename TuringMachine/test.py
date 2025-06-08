class TuringMachine:
    def __init__(self, states, input_alphabet, tape_alphabet, blank_symbol,
                 transition_function, start_state, accept_states, reject_states):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.tape_alphabet = set(tape_alphabet)
        self.blank_symbol = blank_symbol
        self.transition_function = transition_function
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.reject_states = set(reject_states)

    def accepts(self, input_symbols, max_steps=10000):
        for sym in input_symbols:
            if sym not in self.input_alphabet:
                error = f"Input symbol '{sym}' not in input alphabet."
                print(f"[ERROR] {error}")
                return False, error
        tape = list(input_symbols) + [self.blank_symbol] * max(10, len(input_symbols))
        head = 0
        current_state = self.start_state
        steps = 0

        while steps < max_steps:
            steps += 1

            if current_state in self.accept_states:
                return True, None

            if current_state in self.reject_states:
                return False, None

            if head < 0:
                tape.insert(0, self.blank_symbol)
                head = 0

            if head >= len(tape):
                tape.append(self.blank_symbol)

            current_symbol = tape[head]

            if current_symbol not in self.tape_alphabet:
                error = f"Symbol '{current_symbol}' on tape not in tape alphabet."
                print(f"[ERROR] {error}")
                return False, error

            key = (current_state, current_symbol)
            if key not in self.transition_function:
                if current_symbol == self.blank_symbol:
                    info = f"Hit blank at state '{current_state}' — assuming no valid transition."
                    print(f"[INFO] {info}")
                    return False, info
                else:
                    error = f"No transition defined for state '{current_state}' and symbol '{current_symbol}'."
                    print(f"[ERROR] {error}")
                    return False, error

            new_state, write_symbol, direction = self.transition_function[key]

            if write_symbol not in self.tape_alphabet:
                error = f"Write symbol '{write_symbol}' not in tape alphabet."
                print(f"[ERROR] {error}")
                return False, error

            if direction not in ('L', 'R', 'S'):
                error = f"Invalid move direction '{direction}', expected 'L', 'R', or 'S'."
                print(f"[ERROR] {error}")
                return False, error

            tape[head] = write_symbol
            current_state = new_state

            if direction == 'L':
                head -= 1
            elif direction == 'R':
                head += 1
            # 'S' no move

        error = "Max steps exceeded without halting."
        print(f"[ERROR] {error}")
        return False, error


def parse_tm_config(filename):
    sections = {
        "states": [],
        "input_alphabet": [],
        "tape_alphabet": [],
        "blank": None,
        "start": None,
        "accept": [],
        "reject": [],
        "transitions": []
    }

    with open(filename, "r") as f:
        lines = []
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            # Remove inline comments
            if "#" in line:
                line = line.split("#")[0].strip()
            if line:
                lines.append(line)

    current_section = None
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.endswith(":"):
            current_section = line[:-1].strip()
            i += 1
            section_lines = []
            while i < len(lines) and not lines[i].endswith(":"):
                section_lines.append(lines[i])
                i += 1

            if current_section in ["states", "input_alphabet", "tape_alphabet", "accept", "reject"]:
                # Flatten multiline into tokens
                all_items = " ".join(section_lines).split()
                sections[current_section] = all_items
            elif current_section in ["blank", "start"]:
                if section_lines:
                    sections[current_section] = section_lines[0]
            elif current_section == "transitions":
                for tline in section_lines:
                    parts = tline.split()
                    if len(parts) == 5:
                        # Format: current_state current_symbol new_state write_symbol direction
                        cur_st, cur_sym, new_st, write_sym, direction = parts
                        sections["transitions"].append((cur_st, cur_sym, new_st, write_sym, direction))
                    else:
                        print(f"[WARNING] Invalid transition line: '{tline}'")
            else:
                # unknown section, just skip
                pass
        else:
            i += 1

    # Build transitions dict
    transitions = {}
    for cur_st, cur_sym, new_st, write_sym, direction in sections["transitions"]:
        key = (cur_st, cur_sym)
        transitions[key] = (new_st, write_sym, direction)

    # Validate mandatory fields
    required = ["states", "input_alphabet", "tape_alphabet", "blank", "start", "accept"]
    missing = [field for field in required if not sections[field]]
    if missing:
        raise ValueError(f"Missing required TM components in config: {missing}")

    if sections["blank"] not in sections["tape_alphabet"]:
        raise ValueError(f"Blank symbol '{sections['blank']}' must be in tape alphabet.")

    return TuringMachine(
        states=sections["states"],
        input_alphabet=sections["input_alphabet"],
        tape_alphabet=sections["tape_alphabet"],
        blank_symbol=sections["blank"],
        transition_function=transitions,
        start_state=sections["start"],
        accept_states=sections["accept"],
        reject_states=sections.get("reject", [])
    )


if __name__ == "__main__":
    try:
        tm = parse_tm_config("tm_config.txt")
    except Exception as e:
        print("[FATAL ERROR] Failed to build TM:", e)
        exit(1)

    try:
        with open("input.txt", "r") as f:
            input_str = f.read().strip()
            input_symbols = input_str.split()
    except FileNotFoundError:
        print("[FATAL ERROR] 'input.txt' not found.")
        exit(1)

    print(f"[INFO] Input symbols: {input_symbols}")
    result, error = tm.accepts(input_symbols)
    if result:
        print("Accepted")
    else:
        if error:
            print(f"Rejected due to: {error}")
        else:
            print("Rejected")
