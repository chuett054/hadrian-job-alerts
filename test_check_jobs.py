import json
import unittest
from pathlib import Path

from check_jobs import build_digest, is_match, required_years

CONFIG = json.loads((Path(__file__).parent / "config.json").read_text())


def job(title, description="", employment="FullTime", listed=True):
    return {
        "title": title,
        "descriptionPlain": description,
        "employmentType": employment,
        "isListed": listed,
    }


class RequiredYearsTest(unittest.TestCase):
    def test_reads_common_formats(self):
        self.assertEqual(required_years("5+ years of experience"), 5)
        self.assertEqual(required_years("2-5 years experience"), 2)
        self.assertEqual(required_years("10-15+ years"), 10)
        self.assertEqual(required_years("1 year of experience"), 1)

    def test_uses_highest_minimum(self):
        self.assertEqual(required_years("5+ years overall, at least 3+ years in hardware"), 5)

    def test_unstated_is_zero(self):
        self.assertEqual(required_years("Ship great products"), 0)


class IsMatchTest(unittest.TestCase):
    def assertMatch(self, *args, **kwargs):
        self.assertTrue(is_match(job(*args, **kwargs), CONFIG))

    def assertNoMatch(self, *args, **kwargs):
        self.assertFalse(is_match(job(*args, **kwargs), CONFIG))

    def test_product_roles_without_a_high_bar_match(self):
        self.assertMatch("Global Product Manager")
        self.assertMatch("Product Manager", "2+ years of experience")
        self.assertMatch("Technical Program Manager, Factory", "1-3 years")

    def test_experience_bar_excludes_unlabeled_roles(self):
        self.assertNoMatch("Product Manager", "5+ years of product management experience")
        self.assertNoMatch("Technical Program Manager, Infra", "5+ years in TPM")

    def test_early_career_titles_skip_the_experience_bar(self):
        self.assertMatch("Product Manager Intern", "5 years of history", employment="Intern")
        self.assertMatch("Associate Product Manager", "3+ years preferred")
        self.assertMatch("All Levels: Product Manager", "5+ years for senior candidates")

    def test_senior_titles_are_excluded(self):
        for title in ("Senior Product Manager", "Sr. Product Manager", "Lead Product Manager",
                      "Group Product Manager", "Head of Product Management"):
            self.assertNoMatch(title)

    def test_adjacent_roles_are_excluded(self):
        for title in ("Product Engineer", "Senior Product Designer", "Product Marketing Lead",
                      "Program Manager", "Software Engineer Intern"):
            self.assertNoMatch(title)

    def test_unlisted_roles_are_excluded(self):
        self.assertNoMatch("Product Manager", listed=False)


class DigestTest(unittest.TestCase):
    def test_mentions_user_and_links_role(self):
        digest = build_digest(
            [{"title": "Product Manager", "jobUrl": "https://example.com/1",
              "location": "Los Angeles, CA", "department": "Product"}],
            "someone",
        )
        self.assertIn("@someone", digest)
        self.assertIn("[Product Manager](https://example.com/1)", digest)


if __name__ == "__main__":
    unittest.main()
