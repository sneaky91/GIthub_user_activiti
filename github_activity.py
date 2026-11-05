import json
import re
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from translations import translate


API_URL = "https://api.github.com"


class GitHubError(Exception):
    pass


def get_json(path, token=None, language="en"):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GithubUserActivity",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(API_URL + path, headers=headers)

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        error.close()
        if error.code == 404:
            raise GitHubError(translate("not_found", language)) from error
        if error.code == 401:
            raise GitHubError(translate("invalid_token", language)) from error
        if error.code in (403, 429):
            raise GitHubError(translate("api_limit", language)) from error
        raise GitHubError(translate("http_error", language, status=error.code)) from error
    except (URLError, TimeoutError, OSError) as error:
        raise GitHubError(translate("connection_error", language)) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise GitHubError(translate("invalid_response", language)) from error


def validate_username(username, language="en"):
    username = username.strip().removeprefix("@")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username):
        raise GitHubError(translate("invalid_username", language))
    if "--" in username:
        raise GitHubError(translate("consecutive_hyphens", language))
    return username


def load_languages(username, token=None, language="en"):
    repositories = get_json(f"/users/{username}/repos?per_page=30&sort=updated", token, language)
    languages = Counter()

    for repository in repositories:
        repository_name = repository["full_name"]
        repository_languages = get_json(f"/repos/{repository_name}/languages", token, language)
        for name, byte_count in repository_languages.items():
            languages[name] += byte_count

    return languages


def load_user(username, token=None, include_languages=True, language="en"):
    username = validate_username(username, language)
    user = get_json(f"/users/{username}", token, language)
    events = get_json(f"/users/{username}/events?per_page=100", token, language)
    languages = Counter()
    language_error = None

    if include_languages:
        try:
            languages = load_languages(username, token, language)
        except GitHubError as error:
            language_error = str(error)

    return {
        "user": user,
        "events": events,
        "languages": languages,
        "language_error": language_error,
    }


def event_text(event, language="en"):
    event_type = event.get("type", "")
    repository = event.get("repo", {}).get("name", "unknown/repository")
    payload = event.get("payload", {})

    if event_type == "PushEvent":
        commit_count = payload.get("size")
        if commit_count is None and "commits" in payload:
            commit_count = len(payload["commits"])
        if commit_count is None:
            return translate("push", language, repository=repository)
        return translate("push_count", language, count=commit_count, repository=repository)

    if event_type == "IssuesEvent":
        action = translate(payload.get("action", "updated"), language)
        title = payload.get("issue", {}).get("title", translate("untitled", language))
        return translate("issue", language, action=action, repository=repository, title=title)

    if event_type == "PullRequestEvent":
        action = translate(payload.get("action", "updated"), language)
        title = payload.get("pull_request", {}).get("title", translate("untitled", language))
        return translate("pull_request", language, action=action, repository=repository, title=title)

    if event_type == "IssueCommentEvent":
        return translate("comment", language, repository=repository)
    if event_type == "CreateEvent":
        object_name = translate(payload.get("ref_type", "object"), language)
        return translate("create", language, object=object_name, repository=repository)
    if event_type == "DeleteEvent":
        object_name = translate(payload.get("ref_type", "object"), language)
        return translate("delete", language, object=object_name, repository=repository)
    if event_type == "WatchEvent":
        return translate("star", language, repository=repository)
    if event_type == "ForkEvent":
        return translate("fork", language, repository=repository)
    if event_type == "ReleaseEvent":
        action = translate(payload.get("action", "updated"), language)
        return translate("release", language, action=action, repository=repository)
    if event_type == "PublicEvent":
        return translate("public", language, repository=repository)

    activity = event_type.removesuffix("Event") or "Activity"
    return translate("activity", language, activity=activity, repository=repository)
