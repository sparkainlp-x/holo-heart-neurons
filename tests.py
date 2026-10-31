"""Tests for holo-heart-neurons v0.1.0. Run: python tests.py"""

import math
import unittest

from heart import (
    HeartNetwork,
    heart_curve_point,
    recall,
    store_pattern,
    to_svg,
)


class TestHeart(unittest.TestCase):
    def test_curve_at_zero(self):
        x, y = heart_curve_point(0.0)
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 5.0)

    def test_network_size_and_pacemaker(self):
        net = HeartNetwork(n=64, seed=42)
        self.assertEqual(len(net.neurons), 64)
        self.assertEqual(len({neu.id for neu in net.neurons}), 64)
        kinds = [neu.kind for neu in net.neurons]
        self.assertEqual(kinds.count("pacemaker"), 1)
        self.assertEqual(
            net.neurons[net.pacemaker_id].kind, "pacemaker"
        )

    def test_edges_symmetric_no_self_loops(self):
        net = HeartNetwork(n=64, seed=42)
        for a, b in net.edges:
            self.assertNotEqual(a, b)
            self.assertIn(b, net.neighbours(a))
            self.assertIn(a, net.neighbours(b))
        for neu in net.neurons:
            self.assertGreaterEqual(len(net.neighbours(neu.id)), 1)

    def test_propagation_reaches_all(self):
        net = HeartNetwork(n=64, seed=42)
        act = net.propagate()
        self.assertEqual(act[net.pacemaker_id], 0.0)
        self.assertEqual(len(act), 64)
        for t in act.values():
            self.assertTrue(math.isfinite(t))
            self.assertGreaterEqual(t, 0.0)

    def test_beat_glow_at_activation(self):
        net = HeartNetwork(n=32, seed=7)
        act = net.propagate()
        state = net.beat_state(act, t=act[net.pacemaker_id])
        self.assertAlmostEqual(state[net.pacemaker_id], 1.0)
        # Long after the beat, in a long period, glow has faded.
        late = net.beat_state(act, t=act[net.pacemaker_id] + 1000.0,
                              period=10000.0, width=2.0)
        self.assertLess(late[net.pacemaker_id], 0.05)

    def test_holographic_recall_self(self):
        pattern = [1.0 if i % 3 == 0 else 0.0 for i in range(16)]
        W = store_pattern([pattern])
        out = recall(W, pattern)
        # For a single stored pattern, recall(pattern) = pattern * |pattern|^2.
        norm2 = sum(v * v for v in pattern)
        for i, v in enumerate(pattern):
            self.assertAlmostEqual(out[i], v * norm2)

    def test_determinism(self):
        a = HeartNetwork(n=48, seed=123)
        b = HeartNetwork(n=48, seed=123)
        for na, nb in zip(a.neurons, b.neurons):
            self.assertEqual((na.x, na.y, na.kind), (nb.x, nb.y, nb.kind))
        self.assertEqual(a.edges, b.edges)

    def test_svg_frame(self):
        net = HeartNetwork(n=32, seed=42)
        act = net.propagate()
        svg = to_svg(net, act, t=0.0)
        self.assertIn("<svg", svg)
        self.assertIn('fill="black"', svg)
        self.assertEqual(svg.count("<circle"), 32)


if __name__ == "__main__":
    unittest.main(verbosity=2)
