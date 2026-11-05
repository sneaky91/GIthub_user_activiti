import io
import unittest
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import cli
from github_activity import GitHubError, event_text, get_json, load_user
from translations import TEXT


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.user = {
            "login": "octocat",
            "name": None,
            "bio": None,
            "followers": 10,
            "following": 2,
            "public_repos": 3,
        }

    @patch("github_activity.get_json")
    def test_skip_languages_does_not_request_repositories(self, request):
        request.side_effect = [self.user, []]
        data = load_user(" @octocat ", include_languages=False)
        self.assertEqual(data["user"], self.user)
        self.assertEqual(data["events"], [])
        self.assertEqual(request.call_count, 2)
        self.assertEqual(request.call_args_list[0].args[0], "/users/octocat")

    @patch("github_activity.get_json")
    def test_languages_are_summed_across_repositories(self, request):
        request.side_effect = [
            self.user,
            [],
            [{"full_name": "octocat/one"}, {"full_name": "octocat/two"}],
            {"Python": 100, "Shell": 20},
            {"Python": 50},
        ]
        data = load_user("octocat")
        self.assertEqual(data["languages"], {"Python": 150, "Shell": 20})
        self.assertIsNone(data["language_error"])

    @patch("github_activity.get_json")
    def test_language_failure_preserves_profile_and_events(self, request):
        events = [{"type": "WatchEvent", "repo": {"name": "owner/repo"}}]
        request.side_effect = [self.user, events, GitHubError("API limit reached")]
        data = load_user("octocat")
        self.assertEqual(data["user"], self.user)
        self.assertEqual(data["events"], events)
        self.assertEqual(data["language_error"], "API limit reached")

    @patch("github_activity.get_json")
    def test_invalid_username_is_rejected_before_request(self, request):
        for username in ("", "../repos", "name?query", "-name", "name--name"):
            with self.subTest(username=username):
                with self.assertRaises(GitHubError):
                    load_user(username)
        request.assert_not_called()

    @patch("github_activity.urlopen")
    def test_http_and_connection_errors_are_readable(self, open_url):
        for status in (401, 403, 404, 429, 500):
            with self.subTest(status=status):
                open_url.side_effect = HTTPError("https://api.github.com", status, "error", {}, None)
                with self.assertRaises(GitHubError):
                    get_json("/users/octocat")
        open_url.side_effect = URLError("offline")
        with self.assertRaisesRegex(GitHubError, "connect"):
            get_json("/users/octocat")

    @patch("github_activity.urlopen")
    def test_invalid_json_is_reported(self, open_url):
        open_url.return_value.__enter__.return_value.read.return_value = b"not json"
        with self.assertRaisesRegex(GitHubError, "invalid response"):
            get_json("/users/octocat")

    def test_push_without_count_does_not_invent_a_commit(self):
        event = {"type": "PushEvent", "repo": {"name": "owner/repo"}, "payload": {}}
        self.assertEqual(event_text(event), "Pushed commits to owner/repo")
        event["payload"] = {"size": 5, "commits": [{"sha": "one"}]}
        self.assertEqual(event_text(event), "Pushed 5 commit(s) to owner/repo")

    @patch("sys.argv", ["cli.py", "octocat", "--no-languages"])
    @patch("cli.load_user")
    def test_cli_prints_empty_activity_without_language_section(self, load):
        load.return_value = {
            "user": self.user,
            "events": [],
            "languages": Counter(),
            "language_error": None,
        }
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli.main(), 0)
        self.assertIn("octocat (@octocat)", output.getvalue())
        self.assertIn("No recent public activity", output.getvalue())
        self.assertNotIn("Top languages", output.getvalue())

    @patch("sys.argv", ["cli.py", "octocat"])
    @patch("cli.load_user", side_effect=GitHubError("User not found"))
    def test_cli_returns_nonzero_on_api_error(self, load):
        output = io.StringIO()
        with redirect_stderr(output), redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(), 1)
        self.assertEqual(output.getvalue().strip(), "Error: User not found")

    @patch("sys.argv", ["cli.py", "octocat"])
    def test_english_is_default(self):
        self.assertEqual(cli.parse_arguments().language, "en")

    @patch("sys.argv", ["cli.py", "octocat", "--language", "uk", "--no-languages"])
    @patch("cli.load_user")
    def test_ukrainian_profile_and_activity(self, load):
        load.return_value = {
            "user": self.user,
            "events": [{"type": "WatchEvent", "repo": {"name": "owner/repo"}}],
            "languages": Counter(),
            "language_error": None,
        }
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli.main(), 0)
        self.assertIn("Підписники: 10", output.getvalue())
        self.assertIn("Додано зірку до owner/repo", output.getvalue())
        self.assertEqual(load.call_args.args[-1], "uk")

    @patch("github_activity.urlopen")
    def test_ukrainian_api_error(self, open_url):
        open_url.side_effect = HTTPError("https://api.github.com", 404, "error", {}, None)
        with self.assertRaisesRegex(GitHubError, "не знайдено"):
            get_json("/users/octocat", language="uk")

    def test_translations_have_matching_keys(self):
        self.assertEqual(set(TEXT["en"]), set(TEXT["uk"]))

    @patch("cli.supports_color", return_value=True)
    def test_banner_uses_orange_and_resets_color(self, color):
        output = io.StringIO()
        with redirect_stdout(output):
            cli.print_banner()
        self.assertIn("Github User activity", output.getvalue())
        self.assertIn("\033[1;38;2;255;165;0m", output.getvalue())
        self.assertTrue(output.getvalue().endswith("\033[0m\n"))

    def test_redirected_banner_has_no_escape_sequences(self):
        output = io.StringIO()
        with redirect_stdout(output):
            cli.print_banner()
        self.assertIn("Github User activity", output.getvalue())
        self.assertNotIn("\033", output.getvalue())


if __name__ == "__main__":
    unittest.main()
