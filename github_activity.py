"""GitHub API client and statistics used by both the CLI and GUI."""
from collections import Counter
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import json

API = "https://api.github.com"


class GitHubError(Exception):
    pass


def get_json(path, token=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "GitHubUserActivity/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        request = Request(API + path, headers=headers)
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise GitHubError("Пользователь не найден")
        if exc.code == 403:
            raise GitHubError("GitHub API ограничил запросы. Попробуйте позже или укажите GITHUB_TOKEN.")
        raise GitHubError(f"GitHub API вернул ошибку {exc.code}")
    except (URLError, TimeoutError) as exc:
        raise GitHubError(f"Не удалось подключиться к GitHub: {exc.reason if hasattr(exc, 'reason') else exc}")
    except json.JSONDecodeError:
        raise GitHubError("GitHub вернул некорректный ответ")


def _date(value):
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return value


def event_text(event):
    kind = event.get("type", "")
    repo = event.get("repo", {}).get("name", "unknown/repository")
    payload = event.get("payload", {})
    if kind == "PushEvent":
        count = len(payload.get("commits", [])) or payload.get("size", 1)
        return f"Pushed {count} commit(s) to {repo}"
    if kind == "IssuesEvent":
        action = payload.get("action", "updated")
        return f"{action.capitalize()} issue in {repo}: {payload.get('issue', {}).get('title', 'без названия')}"
    if kind == "PullRequestEvent":
        action = payload.get("action", "updated")
        return f"{action.capitalize()} pull request in {repo}: {payload.get('pull_request', {}).get('title', 'без названия')}"
    if kind == "IssueCommentEvent":
        return f"Commented on an issue in {repo}"
    if kind == "CreateEvent":
        return f"Created {payload.get('ref_type', 'object')} in {repo}"
    if kind == "DeleteEvent":
        return f"Deleted {payload.get('ref_type', 'object')} in {repo}"
    if kind == "WatchEvent":
        return f"Starred {repo}"
    if kind == "ForkEvent":
        return f"Forked {repo}"
    if kind == "ReleaseEvent":
        return f"Published a release in {repo}"
    if kind == "PublicEvent":
        return f"Made {repo} public"
    return kind.replace("Event", "") or "Activity"


def load_user(username, token=None, include_languages=True):
    username = username.strip().lstrip("@")
    if not username:
        raise GitHubError("Введите имя пользователя")
    user = get_json(f"/users/{username}", token)
    events = get_json(f"/users/{username}/events?per_page=100", token)
    repos = get_json(f"/users/{username}/repos?per_page=100&sort=updated", token)
    languages = Counter()
    if include_languages:
        for repo in repos[:30]:
            try:
                for language, bytes_count in get_json(repo["languages_url"].replace(API, ""), token).items():
                    languages[language] += bytes_count
            except GitHubError:
                continue
    event_counts = Counter(e.get("type", "Other").replace("Event", "") for e in events)
    push_count = sum(1 for e in events if e.get("type") == "PushEvent")
    return {
        "user": user,
        "events": events,
        "repos": repos,
        "languages": languages,
        "event_counts": event_counts,
        "contributions": len(events),
        "pushes": push_count,
        "fetched_at": datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC"),
    }


def load_repository(reference, token=None):
    """Load repository metadata and language statistics from a URL or owner/name."""
    reference = reference.strip().rstrip("/")
    if reference.startswith("http://") or reference.startswith("https://"):
        parsed = urlparse(reference)
        if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            raise GitHubError("Укажите ссылку на github.com")
        parts = [part for part in parsed.path.split("/") if part]
    else:
        parts = [part for part in reference.split("/") if part]
    if len(parts) != 2 or any(part in {".", ".."} for part in parts):
        raise GitHubError("Формат репозитория: owner/repository или https://github.com/owner/repository")
    owner, name = parts
    repo = get_json(f"/repos/{owner}/{name}", token)
    languages = get_json(f"/repos/{owner}/{name}/languages", token)
    return {"repo": repo, "languages": languages}
