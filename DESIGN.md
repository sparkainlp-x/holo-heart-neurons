# DESIGN.md — holo-heart-neurons v0.1.0

## Decisions

- **Classic heart curve, not a traced image.** The parametric curve
  (16 sin^3, 13 cos − 5 cos2 − 2 cos3 − cos4) is exact, reproducible,
  and test-pinned at t=0 → (0, 5). A traced anatomical outline would
  be prettier and less checkable.
- **Pacemaker = outline neuron nearest the top notch.** No anatomy
  is claimed: the SA node is a real structure with a real location,
  and this package does not model it. The pacemaker here is simply
  a defined beat source, chosen by a rule anyone can re-run.
- **k-nearest-neighbour edges (k=4), not a grid.** A grid would
  fight the heart shape; k-NN follows it, stays connected at this
  size, and keeps every neuron reachable (tested).
- **Dijkstra, not a wave equation.** Activation time = shortest-path
  distance / velocity is the simplest honest propagation rule. It
  gives a clean, testable spread; it does not model conduction
  velocity heterogeneity, refractoriness, or re-entry.
- **Outer-product memory, membrane-style.** W = sum p p^T is the
  same storage rule as the membrane packages, in real vectors.
  It is included because Jean's frame is holographic memory, not
  because a heart "stores" beats this way.
- **SVG frame, not video.** A single SVG at time t is checkable in
  a browser and in a test (circle count = neuron count). Video
  would hide the model behind rendering.

## Falsified / rejected designs

- **Neurons only on the outline.** Rejected: a hollow ring does not
  read as a heart full of neurons, and the interior is where the
  earlier AI image puts most of its network.
- **Random edges.** Rejected: random wiring breaks the heart shape
  and can disconnect neurons; k-NN preserves locality.
- **Real cardiac model (Hodgkin–Huxley, ionic currents).**
  Rejected for v0.1.0: it would pretend to a physiology this
  package does not have data for. A toy beat is honest; a fake
  ECG would not be.
- **Claiming the SVG is a hologram.** Rejected: it is a fan-style
  2D frame. A true hologram needs wavefront reconstruction
  (see the wave-hologram package, a different meaning of the word).

## Limits, restated

Synthetic only. No medical use. No real heart or brain data.
Activation times are in distance units at velocity 1.0, not
milliseconds. Lifespan, brightness, and fan display of the SVG
depend on the display device, not on this code.
