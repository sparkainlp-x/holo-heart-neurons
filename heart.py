"""holo-heart-neurons v0.1.0 — a holographic heart made of neurons.

sparkainlp-x frame: stdlib-only Python, seeded, reproducible, AGPL-3.0-only.

Model, in plain words
---------------------
* A heart outline from the classic parametric heart curve.
* Neurons placed on that outline and inside it (seeded, deterministic).
* Each neuron connects to its k nearest neighbours — a neural net
  shaped like a heart, not a picture of a real heart.
* A beat starts at a pacemaker neuron and spreads along the edges.
  Activation time of a neuron = shortest-path distance from the
  pacemaker, divided by a conduction velocity (Dijkstra).
* "Holographic" here follows the sparkainlp-x membrane frame:
  a beat pattern can be stored as an outer-product memory
  W = sum_p p p^T, and recalled by correlation — the same
  W = sum |p><p| idea as the membrane packages, in real vectors.

What this is NOT: not a cardiac model, not a medical device, not a
measurement of a real heart or brain. Synthetic, toy, educational.
The earlier AI image (holographic heart with neurons, cyan on black)
is the visual reference; this code is the runnable frame behind it.
"""

import heapq
import math
import random

__version__ = "0.1.0"


def heart_curve_point(t):
    """Classic parametric heart curve point at angle t (radians).

    x = 16 sin^3(t)
    y = 13 cos(t) - 5 cos(2t) - 2 cos(3t) - cos(4t)
    At t=0 this gives (0, 5) — checked by a test.
    """
    return (
        16.0 * math.sin(t) ** 3,
        13.0 * math.cos(t)
        - 5.0 * math.cos(2.0 * t)
        - 2.0 * math.cos(3.0 * t)
        - math.cos(4.0 * t),
    )


def _point_in_polygon(x, y, polygon):
    """Ray-casting point-in-polygon test (polygon = list of (x, y))."""
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            x_int = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < x_int:
                inside = not inside
    return inside


class Neuron:
    """One neuron: an id, a position, and a kind."""

    def __init__(self, nid, x, y, kind):
        self.id = nid
        self.x = float(x)
        self.y = float(y)
        self.kind = kind  # 'pacemaker', 'outline', or 'inner'

    def __repr__(self):
        return f"Neuron({self.id}, {self.x:.2f}, {self.y:.2f}, {self.kind!r})"


class HeartNetwork:
    """A heart-shaped neuron network, built deterministically."""

    def __init__(self, n=64, seed=42, outline_frac=0.6, k=4):
        if n < 8:
            raise ValueError("n must be at least 8")
        if not (0.0 < outline_frac < 1.0):
            raise ValueError("outline_frac must be strictly between 0 and 1")
        self.n = n
        self.seed = seed
        self.k = k
        rng = random.Random(seed)

        n_outline = max(4, int(round(n * outline_frac)))
        n_inner = n - n_outline

        # Outline: evenly spaced points on the heart curve.
        outline = [
            heart_curve_point(2.0 * math.pi * i / n_outline)
            for i in range(n_outline)
        ]
        neurons = [
            Neuron(i, x, y, "outline") for i, (x, y) in enumerate(outline)
        ]

        # Inner: seeded points inside the outline polygon.
        inner = []
        attempts = 0
        while len(inner) < n_inner and attempts < 20000:
            attempts += 1
            x = rng.uniform(-17.0, 17.0)
            y = rng.uniform(-17.0, 14.0)
            if _point_in_polygon(x, y, outline):
                inner.append((x, y))
        # Fallback (should not happen): jitter outline points inward.
        while len(inner) < n_inner:
            x, y = outline[len(inner) % n_outline]
            inner.append((x * 0.5, y * 0.5))
        for j, (x, y) in enumerate(inner):
            neurons.append(Neuron(n_outline + j, x, y, "inner"))

        # Pacemaker: the outline neuron closest to the top notch (0, 5).
        # The classic curve's top centre is near there; the nearest
        # outline neuron becomes the beat source.
        pacemaker = min(
            neurons,
            key=lambda neu: (neu.x - 0.0) ** 2 + (neu.y - 5.0) ** 2,
        )
        pacemaker.kind = "pacemaker"
        self.pacemaker_id = pacemaker.id

        self.neurons = neurons
        self.edges = self._connect(k)

    def _connect(self, k):
        """Undirected k-nearest-neighbour edges, no self-loops."""
        edges = set()
        for a in self.neurons:
            dists = sorted(
                (
                    (a.x - b.x) ** 2 + (a.y - b.y) ** 2,
                    b.id,
                )
                for b in self.neurons
                if b.id != a.id
            )
            for _, bid in dists[:k]:
                edges.add((min(a.id, bid), max(a.id, bid)))
        return sorted(edges)

    def neighbours(self, nid):
        """Neighbour ids of neuron nid."""
        out = []
        for a, b in self.edges:
            if a == nid:
                out.append(b)
            elif b == nid:
                out.append(a)
        return sorted(out)

    def propagate(self, source=None, velocity=1.0):
        """Dijkstra activation times from source (default: pacemaker).

        Edge weight = Euclidean distance / velocity. Returns a dict
        {neuron_id: activation_time}. Source time is exactly 0.
        Every neuron is reached, because k-nearest-neighbour graphs
        at k >= 2 are connected in practice for these layouts; if a
        node were unreachable its time would be inf, and the tests
        would catch it.
        """
        if source is None:
            source = self.pacemaker_id
        if velocity <= 0:
            raise ValueError("velocity must be positive")
        by_id = {neu.id: neu for neu in self.neurons}
        times = {neu.id: math.inf for neu in self.neurons}
        times[source] = 0.0
        heap = [(0.0, source)]
        while heap:
            t, nid = heapq.heappop(heap)
            if t > times[nid]:
                continue
            a = by_id[nid]
            for mid in self.neighbours(nid):
                b = by_id[mid]
                w = math.hypot(a.x - b.x, a.y - b.y) / velocity
                if t + w < times[mid]:
                    times[mid] = t + w
                    heapq.heappush(heap, (times[mid], mid))
        return times

    def beat_state(self, activation, t, period=10.0, width=2.0):
        """Per-neuron glow at time t: 0.0 (dark) to 1.0 (bright).

        A neuron glows after its activation, fading exponentially
        over `width`, and the whole beat repeats every `period`.
        At t == activation the glow is exactly 1.0.
        """
        state = {}
        for nid, act in activation.items():
            phase = (t - act) % period
            if phase < 0:
                phase += period
            state[nid] = math.exp(-phase / width) if phase < width * 4 else 0.0
            # exp(-4) ~ 0.018: keep a tiny tail, never negative.
            if phase >= width * 4:
                state[nid] = 0.0
        return state


def store_pattern(patterns):
    """Outer-product holographic memory W = sum_p p p^T.

    patterns: list of equal-length lists of floats (e.g. 0/1 beat
    patterns). Returns W as a list of lists. This is the membrane
    frame's storage rule, in real vectors.
    """
    if not patterns:
        raise ValueError("need at least one pattern")
    n = len(patterns[0])
    if any(len(p) != n for p in patterns):
        raise ValueError("all patterns must have the same length")
    W = [[0.0] * n for _ in range(n)]
    for p in patterns:
        for i in range(n):
            for j in range(n):
                W[i][j] += p[i] * p[j]
    return W


def recall(W, probe):
    """Recall by correlation: overlap of probe with each stored row.

    Returns a list of overlaps, one per neuron index. A stored
    pattern recalled with itself scores highest against itself —
    pinned by a test (it is the diagonal of W for a single pattern).
    """
    n = len(probe)
    if len(W) != n or any(len(row) != n for row in W):
        raise ValueError("W and probe shapes must match")
    return [sum(W[i][j] * probe[j] for j in range(n)) for i in range(n)]


def to_svg(network, activation, t, width=1000, height=1000):
    """One fan-style SVG frame: black background, cyan heart + neurons.

    Coordinates are mapped with X = 500 + x*27, Y = 500 - y*27, so the
    heart (roughly x in [-16, 16], y in [-17, 13]) fits the frame.
    Glow at time t comes from network.beat_state().
    """
    state = network.beat_state(activation, t)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="black"/>',
    ]
    # Edges, faint, brighter when both ends glow.
    by_id = {neu.id: neu for neu in network.neurons}
    for a, b in network.edges:
        na, nb = by_id[a], by_id[b]
        glow = (state[a] + state[b]) / 2.0
        opacity = 0.08 + 0.55 * glow
        parts.append(
            f'<line x1="{500 + na.x * 27:.1f}" y1="{500 - na.y * 27:.1f}" '
            f'x2="{500 + nb.x * 27:.1f}" y2="{500 - nb.y * 27:.1f}" '
            f'stroke="#22d3ee" stroke-width="1" opacity="{opacity:.2f}"/>'
        )
    # Neurons.
    for neu in network.neurons:
        glow = state[neu.id]
        r = 10.0 if neu.kind == "pacemaker" else 4.0 + 6.0 * glow
        fill = "#f472b6" if neu.kind == "pacemaker" else "#22d3ee"
        opacity = 0.45 + 0.55 * glow
        parts.append(
            f'<circle cx="{500 + neu.x * 27:.1f}" cy="{500 - neu.y * 27:.1f}" '
            f'r="{r:.1f}" fill="{fill}" opacity="{opacity:.2f}"/>'
        )
    parts.append("</svg>")
    return "\n".join(parts)
