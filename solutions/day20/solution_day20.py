import time
import logging
from enum import Enum
from abc import ABC


logging.basicConfig(level=logging.INFO)


class Pulse(Enum):
    LOW = False
    HIGH = True


class Module(ABC):
    def __init__(self, name: str, connections: list[str]):
        self.name = name
        self.connections = connections

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.connections}"


class Broadcaster(Module):
    def __init__(self, connections: list[str]):
        super().__init__("broadcaster", connections)


class FlipFlop(Module):
    def __init__(self, name: str, status: bool, connections: list[str]):
        super().__init__(name, connections)
        self.status = status

    def flip(self):
        self.status = True if not self.status else False

    def __repr__(self):
        return f"{super().__repr__()}, {self.status}"


class Conjunction(Module):
    def __init__(self, name: str, connections: list[str]):
        super().__init__(name, connections)
        self.connection_history = {}

    def __repr__(self):
        return f"{super().__repr__()}, {self.connection_history}"


class Untyped(Module):
    def __init__(self, name: str):
        super().__init__(name, [])


def load(file):
    with open(file, "r") as f:
        return [row.strip() for row in f]


def parse(p):
    config = {}
    for row in p:
        row_split = row.split()
        connections = [conn.replace(",", "") for conn in row_split[2:]]
        module_type = row_split[0][0]
        name = row_split[0][1:]
        match module_type:
            case "b":
                config["broadcaster"] = Broadcaster(connections)
            case "%":
                config[name] = FlipFlop(name, False, connections)
            case "&":
                config[name] = Conjunction(name, connections)

    untyped_module_names = []
    for name, module in config.items():
        for conn in module.connections:
            if conn in config:
                continue
            untyped_module_names.append(conn)
        if not isinstance(module, Conjunction):
            continue
        curr_name = module.name
        for name2, module2 in config.items():
            if curr_name in module2.connections:
                config[curr_name].connection_history[name2] = Pulse.LOW  #

    for untyped_module in untyped_module_names:
        config[untyped_module] = Untyped(untyped_module)

    # for name, module in config.items():
    #     print(name, module)
    return config


def iteration(config):
    # if any(Counter(config) == Counter(c) for c in cache):
    #     return cache[config]
    low_pulses, high_pulses = 0, 0
    q = [(config["broadcaster"], Pulse.LOW)]
    conjunction_queue = []
    logging.debug("\n")
    logging.debug(f"button -{Pulse.LOW}-> broadcaster")
    while q:
        module, pulse = q.pop(0)
        if pulse == Pulse.LOW:
            low_pulses += 1
        else:
            high_pulses += 1
        if isinstance(module, Broadcaster):
            for conn in module.connections:
                q.append((config[conn], pulse))
                logging.debug(f"{module.name} -{pulse}-> {conn}")
        elif isinstance(module, FlipFlop):
            if pulse == Pulse.HIGH:
                continue
            config[module.name].flip()
            for conn in module.connections:
                if config[module.name].status:
                    q.append((config[conn], Pulse.HIGH))
                    logging.debug(f"{module.name} -{Pulse.HIGH}-> {conn}")
                else:
                    q.append((config[conn], Pulse.LOW))
                    logging.debug(f"{module.name} -{Pulse.LOW}-> {conn}")
        elif isinstance(module, Conjunction):
            module.connection_history[conjunction_queue.pop(0)] = pulse
            if all(pulse == Pulse.HIGH for pulse in module.connection_history.values()):
                for conn in module.connections:
                    q.append((config[conn], Pulse.LOW))
                    logging.debug(f"{module.name} -{Pulse.LOW}-> {conn}")
            else:
                for conn in module.connections:
                    if conn in config:
                        q.append((config[conn], Pulse.HIGH))
                    logging.debug(f"{module.name} -{Pulse.HIGH}-> {conn}")
        elif isinstance(module, Untyped):
            continue

        for conn in module.connections:
            if isinstance(config[conn], Conjunction):
                conjunction_queue.append(module.name)

    # cache[Counter(config)] = (low_pulses, high_pulses)
    # print(cache)
    return low_pulses, high_pulses


def solve(p):
    config = parse(p)
    low_pulses_count = high_pulses_count = 0
    # cache = {}
    for _ in range(1000):
        low_pulses, high_pulses = iteration(config)
        low_pulses_count += low_pulses
        high_pulses_count += high_pulses
    return low_pulses_count * high_pulses_count


if __name__ == "__main__":
    time_start = time.perf_counter()
    solution = solve(load("puzzle_input_day20.txt"))
    print(f"Part 1: {solution}")
    print(f"Solved in {time.perf_counter() - time_start:.5f} Sec.")
