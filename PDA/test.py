class PDA:
    def __init__(self, states, alphabet, stack_alphabet, transitions, start_state, start_stack_symbol, accept_states):
        self.states = set(states)
        self.alphabet = set(alphabet)  # now alphabet holds strings, not single chars
        self.stack_alphabet = set(stack_alphabet)
        self.transitions = transitions  # dict: (state, input_symbol, stack_top) -> list of (next_state, stack_push_list)
        self.start_state = start_state
        self.start_stack_symbol = start_stack_symbol
        self.accept_states = set(accept_states)

    def accepts(self, input_string):
        # Split input string by spaces, to get each symbol as a string
        input_symbols = input_string.strip().split()

        # Validate symbols
        for symbol in input_symbols:
            if symbol not in self.alphabet:
                print(f"[ERROR] Invalid symbol '{symbol}' in input.")
                return False

        # Configurations = list of tuples: (state, input_index, stack)
        configs = [(self.start_state, 0, [self.start_stack_symbol])]

        while configs:
            state, index, stack = configs.pop()

            # Accept condition: all input consumed, in accept state, stack at start symbol only
            if index == len(input_symbols) and state in self.accept_states and stack == [self.start_stack_symbol]:
                return True

            # Current input symbol or 'e' for epsilon moves
            current_sym = input_symbols[index] if index < len(input_symbols) else 'e'
            stack_top = stack[-1] if stack else 'e'

            possible_keys = [
                (state, current_sym, stack_top),
                (state, current_sym, 'e'),
                (state, 'e', stack_top),
                (state, 'e', 'e'),
            ]

            for key in possible_keys:
                if key in self.transitions:
                    for (next_state, stack_push) in self.transitions[key]:
                        new_stack = stack.copy()
                        # Pop stack if stack_top != epsilon
                        if key[2] != 'e' and new_stack:
                            new_stack.pop()
                        # Push new stack symbols (ignore epsilon)
                        for sym in reversed(stack_push):
                            if sym != 'e':
                                new_stack.append(sym)
                        # Move input index forward only if input symbol != epsilon
                        new_index = index + 1 if key[1] != 'e' else index
                        configs.append((next_state, new_index, new_stack))

        return False


def parse_pda_config(filename):
    sections = {
        "states": [],
        "alphabet": [],
        "stack_alphabet": [],
        "start": None,
        "start_stack": None,
        "accept": [],
        "transitions": []
    }

    with open(filename, "r") as f:
        lines = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
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

            if current_section in ["states", "alphabet", "stack_alphabet", "accept"]:
                # Flatten and split by whitespace, so multi-word symbols can be supported naturally
                all_items = []
                for l in section_lines:
                    all_items.extend(l.split())
                sections[current_section] = all_items

            elif current_section in ["start", "start_stack"]:
                if section_lines:
                    sections[current_section] = section_lines[0]

            elif current_section == "transitions":
                for tline in section_lines:
                    parts = tline.split()
                    if len(parts) >= 4:
                        from_state = parts[0]
                        input_sym = parts[1]
                        stack_top = parts[2]
                        to_state = parts[3]
                        stack_push = parts[4:] if len(parts) > 4 else ['e']
                        sections["transitions"].append((from_state, input_sym, stack_top, to_state, stack_push))
            else:
                # unknown section, ignore
                pass
        else:
            i += 1

    # Build transitions dict with keys as tuples (state, input_symbol, stack_top)
    transitions = {}
    for from_state, input_sym, stack_top, to_state, stack_push in sections["transitions"]:
        key = (from_state, input_sym, stack_top)
        if key not in transitions:
            transitions[key] = []
        transitions[key].append((to_state, stack_push))

    # Validate all main parts exist
    if not (sections["states"] and sections["alphabet"] and sections["stack_alphabet"] and sections["start"] and
            sections["start_stack"] and sections["accept"] and transitions):
        raise ValueError("Missing PDA components in config.")

    return PDA(
        states=sections["states"],
        alphabet=sections["alphabet"],
        stack_alphabet=sections["stack_alphabet"],
        transitions=transitions,
        start_state=sections["start"],
        start_stack_symbol=sections["start_stack"],
        accept_states=sections["accept"]
    )


if __name__ == "__main__":
    try:
        pda = parse_pda_config("pda_config.txt")
    except Exception as e:
        print("[FATAL ERROR] Failed to build PDA:", e)
        exit(1)

    try:
        with open("input.txt") as f:
            input_str = f.read().strip()
    except FileNotFoundError:
        print("[FATAL ERROR] 'input.txt' not found.")
        exit(1)

    print(f"[INFO] Input symbols: {input_str.split()}")
    if pda.accepts(input_str):
        print("Accepted")
    else:
        print("Rejected")
