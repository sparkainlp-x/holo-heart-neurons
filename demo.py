"""Demo for holo-heart-neurons v0.1.0. Run: python demo.py

Builds a 64-neuron heart (seed 42), propagates one beat from the
pacemaker, prints the numbers, and writes holo-heart-demo.svg
(a black-background, cyan fan-style frame at t = 0).
"""

import os

from heart import HeartNetwork, to_svg

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    net = HeartNetwork(n=64, seed=42)
    act = net.propagate()
    times = sorted(act.values())
    print(f"holo-heart-neurons v0.1.0 — {len(net.neurons)} neurons, "
          f"{len(net.edges)} edges")
    print(f"pacemaker: neuron {net.pacemaker_id}")
    print(f"activation: first 0.00, median {times[len(times)//2]:.2f}, "
          f"last {times[-1]:.2f} (distance units, velocity 1.0)")
    print(f"beat: at t=0, pacemaker glow "
          f"{net.beat_state(act, 0.0)[net.pacemaker_id]:.2f}")
    svg = to_svg(net, act, t=0.0)
    path = os.path.join(HERE, "holo-heart-demo.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {path} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
