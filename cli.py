import argparse
import ctypes
import os
import sys

from github_activity import GitHubError, event_text, load_user
from translations import translate


def supports_color():
    if not sys.stdout.isatty() or "NO_COLOR" in os.environ:
        return False
    if os.name == "nt":
        from ctypes import wintypes

        kernel = ctypes.windll.kernel32
        kernel.GetStdHandle.restype = wintypes.HANDLE
        kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        handle = kernel.GetStdHandle(-11)
        mode = wintypes.DWORD()
        if not kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel.SetConsoleMode(handle, mode.value | 4))
    return os.getenv("TERM") != "dumb"


def print_banner():
    banner = "\n  ╭──────────────────────────╮\n  │   Github User activity   │\n  ╰──────────────────────────╯"
    if supports_color():
        banner = f"\033[1;38;2;255;165;0m{banner}\033[0m"
    print(banner, flush=True)


def parse_arguments():
    language_parser = argparse.ArgumentParser(add_help=False)
    language_parser.add_argument("--language", choices=("en", "uk"), default="en")
    language_arguments, _ = language_parser.parse_known_args()
    language = language_arguments.language
    parser = argparse.ArgumentParser(
        prog="GithubUserActivity",
        description=translate("description", language),
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help=translate("help", language))
    parser.add_argument("username", help=translate("username", language))
    parser.add_argument(
        "--language", choices=("en", "uk"), default="en", help=translate("language", language)
    )
    parser.add_argument(
        "--no-languages",
        action="store_true",
        help=translate("skip_languages", language),
    )
    return parser.parse_args()


def print_profile(user, language="en"):
    name = user.get("name") or user["login"]
    print(f"\n{name} (@{user['login']})")
    print(user.get("bio") or translate("no_bio", language))
    print(f"{translate('followers', language)}: {user['followers']}")
    print(f"{translate('following', language)}: {user['following']}")
    print(f"{translate('repositories', language)}: {user['public_repos']}")


def print_languages(languages, error, language="en"):
    print(f"\n{translate('top_languages', language)}")
    if error:
        print(f"  {translate('language_error', language, error=error)}")
        return
    if not languages:
        print(f"  {translate('no_languages', language)}")
        return
    for name, byte_count in languages.most_common(10):
        print(f"  - {name}: {byte_count:,} {translate('bytes', language)}")


def print_activity(events, language="en"):
    print(f"\n{translate('recent_events', language, count=len(events))}")
    if not events:
        print(f"  {translate('no_events', language)}")
        return
    for event in events[:30]:
        date = event.get("created_at", "")[:10]
        print(f"  - {event_text(event, language)} [{date}]")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print_banner()
    arguments = parse_arguments()
    language = arguments.language
    token = os.getenv("GITHUB_TOKEN")

    try:
        data = load_user(arguments.username, token, not arguments.no_languages, language)
    except GitHubError as error:
        print(f"{translate('error', language)}: {error}", file=sys.stderr)
        return 1

    print_profile(data["user"], language)
    if not arguments.no_languages:
        print_languages(data["languages"], data["language_error"], language)
    print_activity(data["events"], language)
    return 0


if __name__ == "__main__":
    sys.exit(main())
