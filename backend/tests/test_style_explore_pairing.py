import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import style_explore_algorithm as algorithm
from app import style_explore_pairing as pairing


class FixedArtistPairingTest(unittest.TestCase):
    def options(self, **patch):
        return pairing.normalize_options({"fixed_artists": [{"id": "lk149", "weight": 1.5}], **patch})

    def test_random_partners_never_duplicate_or_change_fixed_artist(self):
        config = algorithm.WeightSamplingConfig(lower=0.2, upper=0.6, mode=0.4)
        result = pairing.generate_basic(["lk149", "a", "b", "c"], 1, 80, config, random.Random(7), 2, self.options())
        for candidate in result:
            self.assertEqual(candidate.artist_weights[0], algorithm.ArtistWeight("lk149", 1.5))
            self.assertEqual(sum(item.artist_id == "lk149" for item in candidate.artist_weights), 1)
            self.assertTrue(2 <= len(candidate.artist_weights) <= 3)
            self.assertTrue(all(0.2 <= item.weight <= 0.6 for item in candidate.artist_weights[1:]))

    def test_sequential_round_covers_pool_in_order_with_repetitions(self):
        options = self.options(pairing_mode="sequential", samples_per_artist=2)
        pool = ["a", "lk149", "b", "c"]
        count = pairing.round_count(pool, 99, options)
        self.assertEqual(count, 6)
        result = pairing.generate_basic(pool, 2, count, algorithm.WeightSamplingConfig(), random.Random(4), 10, options)
        self.assertEqual([candidate.artist_weights[1].artist_id for candidate in result], ["a", "a", "b", "b", "c", "c"])
        self.assertTrue(all(len(candidate.artist_weights) == 2 for candidate in result))

    def test_deep_mutations_keep_anchor_even_with_single_partner_limit(self):
        parents = [algorithm.DeepParent.from_artist_string("p1", "1.5::lk149 ::, 0.4::a ::")]
        config = algorithm.WeightSamplingConfig(lower=0.2, upper=0.6, mode=0.4)
        result = pairing.generate_deep(parents, ["lk149", "a", "b", "c"], 5, config, random.Random(3), 1, self.options())
        self.assertTrue(all(candidate.artist_weights[0] == algorithm.ArtistWeight("lk149", 1.5) for candidate in result))
        self.assertTrue(all(len(candidate.artist_weights) == 2 for candidate in result))
        self.assertEqual(len({candidate.artist_string for candidate in result}), 5)

    def test_multiple_fixed_artists_and_full_serialization(self):
        options = self.options(fixed_artists=[{"id": "lk149", "weight": 0.8}, {"id": "second", "weight": 0.6}])
        result = pairing.generate_basic(["second", "a", "lk149"], 1, 1, algorithm.WeightSamplingConfig(), random.Random(0), 1, options)[0]
        self.assertEqual([item.artist_id for item in result.artist_weights], ["lk149", "second", "a"])
        self.assertEqual(algorithm.parse_artist_string(result.artist_string), result.artist_weights)

    def test_legacy_random_round_has_identical_candidates(self):
        config = algorithm.WeightSamplingConfig()
        expected = algorithm.generate_basic_candidates(["a", "b", "c"], 1, 10, config, random.Random(42), 3)
        actual = pairing.generate_basic(["a", "b", "c"], 1, 10, config, random.Random(42), 3, pairing.normalize_options({}))
        self.assertEqual(expected, actual)

    def test_invalid_fixed_artists_and_modes_are_rejected(self):
        for raw in [
            {"fixed_artists": [{"id": "", "weight": 0.8}]},
            {"fixed_artists": [{"id": "lk149", "weight": float("nan")}]},
            {"fixed_artists": [{"id": "lk149", "weight": 0.85}]},
            {"fixed_artists": [{"id": "a", "weight": 1}, {"id": "a", "weight": 1}]},
            {"pairing_mode": "other"}, {"samples_per_artist": 1.5}, {"seed_mode": "other"},
        ]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                pairing.normalize_options(raw)

    def test_empty_remaining_pool_and_excessive_round_size_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "没有可搭配"):
            pairing.partner_pool(["lk149"], self.options())
        with self.assertRaisesRegex(ValueError, "1000"):
            pairing.round_count([f"a{i}" for i in range(501)], 1, self.options(pairing_mode="sequential", samples_per_artist=2))

    def test_fixed_seed_zero_and_random_seed_are_frozen(self):
        self.assertEqual(pairing.freeze_comparison_seed(self.options(seed_mode="fixed"), {"seed": 0})["comparison_seed"], 0)
        chosen = pairing.freeze_comparison_seed(self.options(seed_mode="fixed"), {"seed": -1})["comparison_seed"]
        self.assertTrue(0 <= chosen < 2**32)


if __name__ == "__main__":
    unittest.main()
