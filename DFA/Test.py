class DFA:
    def __init__(self, states, alphabet, transition_function, start_state, accept_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transition_function = transition_function
        self.start_state = start_state
        self.accept_states = set(accept_states)

    def accepts(self, input_string):
        current_state = self.start_state
        for symbol in input_string.split():
            if symbol not in self.alphabet:
                raise ValueError(f"[ERROR] Invalid symbol '{symbol}' in input.")
            key = (current_state, symbol)
            if key not in self.transition_function:
                raise ValueError(f"[ERROR] No transition from state '{current_state}' on symbol '{symbol}'.")
            current_state = self.transition_function[key]
        return current_state in self.accept_states


def parse_dfa_config(filename):
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
                    transitions[(from_state, symbol)] = to_state

    if not (alphabet and states and start and accept and transitions):
        raise ValueError("One or more DFA components are missing in the config.")

    return DFA(states, alphabet, transitions, start, accept)


if __name__ == "__main__":
    try:
        dfa = parse_dfa_config("dfa_config.txt")
    except Exception as e:
        print("[FATAL ERROR] Failed to build DFA:", e)
        exit(1)

    try:
        with open("input.txt", "r") as f:
            input_str = f.read().strip()
    except FileNotFoundError:
        print("[FATAL ERROR] 'input.txt' not found.")
        exit(1)

    print(f"[INFO] Input string: '{input_str}'")
    try:
        if dfa.accepts(input_str):
            print("Accepted")
        else:
            print("Rejected")
    except ValueError as err:
        print(err)

