"""Command-line version: python cli.py <github-username>"""
import argparse
import os
import sys
from github_activity import GitHubError, event_text, load_user


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Показать недавнюю активность GitHub-пользователя")
    parser.add_argument("username", help="имя пользователя GitHub")
    parser.add_argument("--no-languages", action="store_true", help="не загружать статистику языков")
    args = parser.parse_args()
    try:
        data = load_user(args.username, os.getenv("GITHUB_TOKEN"), not args.no_languages)
    except GitHubError as exc:
        parser.error(str(exc))
    user = data["user"]
    print(f"\n{user.get('name') or user['login']} (@{user['login']})")
    print(f"{user.get('bio') or 'Без описания'}")
    print(f"Followers: {user['followers']} | Following: {user['following']} | Public repos: {user['public_repos']}")
    print(f"Recent contributions/events: {data['contributions']} | Push events: {data['pushes']}")
    print("\nTop languages (by bytes in the latest repositories):")
    if data["languages"]:
        for name, amount in data["languages"].most_common(10):
            print(f"  - {name}: {amount:,} bytes")
    else:
        print("  Нет данных")
    print("\nRecent activity:")
    if not data["events"]:
        print("  Активность не найдена")
    for event in data["events"][:30]:
        print(f"  - {event_text(event)} [{event.get('created_at', '')[:10]}]")


if __name__ == "__main__":
    main()
