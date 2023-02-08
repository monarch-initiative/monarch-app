from unittest import TestCase, skip

from oaklib import OntologyResource
# commented out until we bring oakx-grape back in
# from oakx_grape.grape_implementation import GrapeImplementation

DB_PATH = "sqlite:obo:bfo"
# DB_PATH = "sqlite:///tests/data/go-nucleus.db"
# move to go-nucleus, add tests/input dir

class TestSemsim(TestCase):
    def setUp(self) -> None:
        self.oi = GrapeImplementation(OntologyResource(slug=DB_PATH))
        self.test_node = "BFO:0000006"

    @skip  # until we have oakx-grape back
    def test_semsim(self):
        label = self.oi.label(self.test_node)

        sim = self.oi.termset_pairwise_similarity([self.test_node], ["BFO:0000002"])

        score = sim.subject_best_matches[self.test_node].score

        self.assertEqual(label, "entity")
        self.assertGreaterEqual(len(sim), 7)
        self.assertGreater(score, 0.04)
