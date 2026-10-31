# holo-heart-neurons v0.1.0

**A holographic heart made of neurons — in code, in the sparkainlp-x frame.**

Stdlib-only Python, seeded, reproducible, AGPL-3.0-only.

The visual reference is the AI image *holographic heart with neurons*
(cyan anatomical heart wired into a neural network, on black).
This package is the runnable frame behind that image: a heart-shaped
neuron network, a beat that spreads from a pacemaker, and a black-background
SVG frame in fan style.

## Run

```bash
python demo.py    # prints the numbers, writes holo-heart-demo.svg
python tests.py   # 8 tests
```

## What it does

- Heart outline from the classic parametric heart curve.
- 64 neurons by default (seed 42): on the outline and inside it.
- Each neuron connects to its 4 nearest neighbours.
- One beat: pacemaker fires, activation spreads by shortest path
  (Dijkstra, edge weight = distance / velocity).
- Beat glow: a neuron glows at its activation, then fades, and the
  beat repeats every period.
- Holographic memory, membrane-style: a beat pattern stored as
  W = sum_p p p^T, recalled by correlation.

## Measured (demo, seed 42, n=64)

- 64 neurons, 156 edges, pacemaker neuron 0
- Activation: first 0.00, median 17.52, last 31.90
  (distance units, velocity 1.0; pacemaker glow 1.00 at t=0)
- Every neuron reached; all activation times finite and ≥ 0

No number here is a medical measurement.

## Honest limits

- **Synthetic toy, not a heart, not a brain, not a medical device.**
  No cardiac electrophysiology, no real neuron data, no calibration.
- "Holographic" here means two distinct things, kept separate:
  (1) the LED-fan-style visual frame (black background, cyan glow),
  (2) the membrane-style outer-product memory. Neither is a laser
  hologram, and neither proves anything about real hearts.
- The SVG is a single frame at one time t. An animation is a
  sequence of frames (call `to_svg` for t = 0, 0.5, 1.0, …), not
  included as video in this package.

## Files

- `heart.py` — model, propagation, beat glow, memory, SVG frame
- `demo.py` — demo + SVG writer
- `tests.py` — 8 tests
- `DESIGN.md` — decisions, falsified designs, limits
- `LICENSE` — AGPL-3.0-only

## Credits

Authors: Jean-François Brisson and Mun Seok Lee.
Lee, author of the Digital to Wave paradigm (Zenodo 21947036,
21947108), is the inspiration friend behind this wave and
membrane work. This package's code was built by Brisson with
AI assistance, except where a file already credits Lee as
author; the joint credit here is for the shared programme,
not a claim that Lee wrote every line of this package.
