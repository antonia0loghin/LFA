class NFA:
    def __init__(self, states, alphabet, transition_function, start_state, accept_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        # transition_function: dict with keys (state, symbol), values = set of next states
        self.transition_function = transition_function
        self.start_state = start_state
        self.accept_states = set(accept_states)

    def accepts(self, input_symbols):
        """
        input_symbols: list of strings, each string is a symbol from the alphabet
        """
        current_states = {self.start_state}  # start with set of states
        for symbol in input_symbols:
            if symbol not in self.alphabet:
                raise ValueError(f"[ERROR] Invalid symbol '{symbol}' in input.")
            next_states = set()
            for state in current_states:
                key = (state, symbol)
                if key in self.transition_function:
                    next_states.update(self.transition_function[key])
            if not next_states:
                raise ValueError(f"[ERROR] No transition from states {current_states} on symbol '{symbol}'.")
            current_states = next_states
        # accept if ANY of current_states is an accept state
        return any(state in self.accept_states for state in current_states)


def parse_nfa_config(filename):
    alphabet = []
    states = []
    start = None
    accept = []
    transitions = {}

    current_section = None
    with open(filename, "r") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#")[0].strip()

            if line.endswith(":"):
                current_section = line[:-1].strip()
                continue

            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                current_section = key
                line = value

            if current_section == "alphabet":
                # Instead of splitting by whitespace, split by commas or spaces?
                # Assuming symbols are separated by spaces still for config
                alphabet.extend(line.split())
            elif current_section == "states":
                states.extend(line.split())
            elif current_section == "start":
                start = line.strip()
            elif current_section == "accept":
                accept.extend(line.split())
            elif current_section == "transitions":
                parts = line.split()
                if len(parts) == 3:
                    from_state, symbol, to_state = parts
                    key = (from_state, symbol)
                    if key not in transitions:
                        transitions[key] = set()
                    transitions[key].add(to_state)

    if not (alphabet and states and start and accept and transitions):
        raise ValueError("One or more NFA components are missing in the config.")

    return NFA(states, alphabet, transitions, start, accept)


if __name__ == "__main__":
    try:
        nfa = parse_nfa_config("nfa_config.txt")
    except Exception as e:
        print("[FATAL ERROR] Failed to build NFA:", e)
        exit(1)

    try:
        with open("input.txt", "r") as f:
            # Split input by whitespace to get list of symbols
            input_symbols = f.read().strip().split()
    except FileNotFoundError:
        print("[FATAL ERROR] 'input.txt' not found.")
        exit(1)

    print(f"[INFO] Input symbols: {input_symbols}")
    try:
        if nfa.accepts(input_symbols):
            print("Accepted")
        else:
            print("Rejected")
    except ValueError as err:
        print(err)
