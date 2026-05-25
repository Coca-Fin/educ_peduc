from pathlib import Path

p = Path(__file__).parent.resolve()

t1 = (1, 2, 3)
t2 = (3, 2, 1)
d = {1: "a", 2: "b"}

print((tuple(d.values())))