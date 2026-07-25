"""Modern, accessible PySide6 GUI for GitHub User Activity."""
import os
import sys
from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
    QProgressBar, QPushButton, QTabWidget, QTextBrowser, QVBoxLayout, QWidget,
)
from github_activity import GitHubError, event_text, load_repository, load_user


STYLESHEET = """
QMainWindow, QWidget { background: #f6f8fa; color: #172033; font-family: 'Segoe UI'; }
QLabel#title { font-size: 28px; font-weight: 700; color: #172033; }
QLabel#subtitle, QLabel#muted { color: #667085; font-size: 13px; }
QLabel#sectionLabel { color: #344054; font-size: 12px; font-weight: 700; }
QLineEdit { background: #ffffff; border: 1px solid #d0d5dd; border-radius: 9px; padding: 11px 13px; color: #172033; font-size: 14px; }
QLineEdit:focus { border: 2px solid #1f883d; padding: 10px 12px; }
QPushButton { background: #1f883d; border: 0; border-radius: 9px; padding: 12px 22px; color: white; font-weight: 700; }
QPushButton:hover { background: #1a7f37; }
QPushButton:pressed { background: #116329; }
QPushButton:disabled { background: #98a2b3; color: #f2f4f7; }
QComboBox { background: #ffffff; border: 1px solid #d0d5dd; border-radius: 8px; padding: 8px 12px; color: #344054; min-width: 108px; }
QComboBox:hover, QComboBox:focus { border-color: #1f883d; }
QComboBox QAbstractItemView { background: white; color: #172033; selection-background-color: #dcfae6; selection-color: #116329; }
QFrame#card { background: #ffffff; border: 1px solid #eaecf0; border-radius: 12px; }
QLabel#cardNumber { color: #172033; font-size: 25px; font-weight: 700; }
QLabel#cardCaption { color: #667085; font-size: 12px; }
QTabWidget::pane { border: 1px solid #eaecf0; border-radius: 12px; background: #ffffff; }
QTabBar::tab { background: transparent; color: #667085; padding: 11px 20px; }
QTabBar::tab:hover { color: #1f883d; }
QTabBar::tab:selected { color: #116329; font-weight: 700; border-bottom: 2px solid #1f883d; }
QTextBrowser, QListWidget { background: #ffffff; border: 0; color: #344054; padding: 14px; font-size: 13px; }
QTextBrowser a { color: #0969da; }
QListWidget::item { padding: 12px 8px; border-bottom: 1px solid #f2f4f7; }
QListWidget::item:hover { background: #f6fef8; }
QProgressBar { background: #eaecf0; border: 0; border-radius: 4px; height: 7px; text-align: right; color: transparent; }
QProgressBar::chunk { background: #1f883d; border-radius: 4px; }
"""

TEXT = {
    "en": {
        "title": "GitHub User Activity", "subtitle": "Profile insights, recent activity and repository statistics",
        "placeholder": "Enter a GitHub username", "load": "Load profile", "ready": "Ready to load",
        "loading": "Loading data from GitHub…", "updated": "Updated", "overview": "Overview",
        "activity": "Activity", "repositories": "Repositories", "events": "Recent events",
        "pushes": "Push events", "repos": "Public repositories", "followers": "Followers",
        "profile": "Profile", "following": "Following", "created": "Account created",
        "languages": "Programming languages", "language_hint": "By code volume in recent repositories",
        "no_languages": "No language data", "no_activity": "No activity found", "no_repos": "No repositories found",
        "no_bio": "No bio", "without_description": "No description", "error_title": "GitHub API error",
        "load_error": "Could not load data", "bytes": "bytes", "stars": "Stars", "forks": "Forks",
        "repo_stats": "Repository Stats", "repo_placeholder": "https://github.com/owner/repository",
        "check_repo": "Check repository", "repo_ready": "Enter a repository URL", "repo_loading": "Loading repository…",
        "repo_profile": "Repository", "description": "Description", "primary_language": "Primary language",
        "watchers": "Watchers", "issues": "Open issues", "repo_languages": "Languages in repository",
        "repo_no_description": "No description", "repo_no_languages": "No language data",
    },
    "uk": {
        "title": "Активність користувача GitHub", "subtitle": "Профіль, остання активність і статистика репозиторіїв",
        "placeholder": "Введіть ім’я користувача GitHub", "load": "Завантажити профіль", "ready": "Готово до завантаження",
        "loading": "Завантаження даних з GitHub…", "updated": "Оновлено", "overview": "Огляд",
        "activity": "Активність", "repositories": "Репозиторії", "events": "Останні події",
        "pushes": "Події push", "repos": "Публічні репозиторії", "followers": "Підписники",
        "profile": "Профіль", "following": "Підписки", "created": "Акаунт створено",
        "languages": "Мови програмування", "language_hint": "За обсягом коду в останніх репозиторіях",
        "no_languages": "Немає даних про мови", "no_activity": "Активність не знайдена", "no_repos": "Репозиторії не знайдені",
        "no_bio": "Немає опису", "without_description": "Без опису", "error_title": "Помилка GitHub API",
        "load_error": "Не вдалося завантажити дані", "bytes": "байт", "stars": "Зірки", "forks": "Форки",
        "repo_stats": "Статистика репозиторію", "repo_placeholder": "https://github.com/owner/repository",
        "check_repo": "Перевірити репозиторій", "repo_ready": "Введіть посилання на репозиторій", "repo_loading": "Завантаження репозиторію…",
        "repo_profile": "Репозиторій", "description": "Опис", "primary_language": "Основна мова",
        "watchers": "Спостерігачі", "issues": "Відкриті issues", "repo_languages": "Мови в репозиторії",
        "repo_no_description": "Немає опису", "repo_no_languages": "Немає даних про мови",
    },
}


class Loader(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username

    def run(self):
        try:
            self.finished.emit(load_user(self.username, os.getenv("GITHUB_TOKEN")))
        except GitHubError as exc:
            self.failed.emit(str(exc))


class RepositoryLoader(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, reference):
        super().__init__()
        self.reference = reference

    def run(self):
        try:
            self.finished.emit(load_repository(self.reference, os.getenv("GITHUB_TOKEN")))
        except GitHubError as exc:
            self.failed.emit(str(exc))


class StatCard(QFrame):
    def __init__(self, caption):
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        self.number = QLabel("—")
        self.number.setObjectName("cardNumber")
        self.label = QLabel(caption)
        self.label.setObjectName("cardCaption")
        layout.addWidget(self.number)
        layout.addWidget(self.label)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub User Activity")
        self.resize(1100, 760)
        self.setMinimumSize(820, 600)
        self.setStyleSheet(STYLESHEET)
        self.lang = "en"
        self.data = None
        self.repo_data = None
        self._build()
        self._translate()

    def t(self, key):
        return TEXT[self.lang][key]

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(34, 28, 34, 28)
        main.setSpacing(16)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("title")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        titles.addWidget(self.title)
        titles.addWidget(self.subtitle)
        header.addLayout(titles, 1)
        self.language = QComboBox()
        self.language.addItem("English", "en")
        self.language.addItem("Українська", "uk")
        self.language.currentIndexChanged.connect(self.change_language)
        header.addWidget(self.language, 0, Qt.AlignTop)
        main.addLayout(header)

        search = QHBoxLayout()
        self.username = QLineEdit("kamranahmedse")
        self.username.returnPressed.connect(self.start_load)
        self.button = QPushButton()
        self.button.clicked.connect(self.start_load)
        search.addWidget(self.username)
        search.addWidget(self.button)
        main.addLayout(search)
        self.status = QLabel()
        self.status.setObjectName("muted")
        main.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        main.addWidget(self.progress)

        cards = QGridLayout()
        cards.setSpacing(12)
        self.cards = [StatCard(""), StatCard(""), StatCard(""), StatCard("")]
        for index, card in enumerate(self.cards):
            cards.addWidget(card, 0, index)
        main.addLayout(cards)

        self.tabs = QTabWidget()
        self.overview = QTextBrowser()
        self.overview.setOpenExternalLinks(True)
        self.activity_list = QListWidget()
        self.repositories_list = QListWidget()
        self.repo_stats = QWidget()
        repo_layout = QVBoxLayout(self.repo_stats)
        repo_layout.setContentsMargins(18, 18, 18, 18)
        repo_search = QHBoxLayout()
        self.repo_reference = QLineEdit("https://github.com/kamranahmedse/developer-roadmap")
        self.repo_reference.returnPressed.connect(self.start_repo_load)
        self.repo_button = QPushButton()
        self.repo_button.clicked.connect(self.start_repo_load)
        repo_search.addWidget(self.repo_reference)
        repo_search.addWidget(self.repo_button)
        repo_layout.addLayout(repo_search)
        self.repo_status = QLabel()
        self.repo_status.setObjectName("muted")
        repo_layout.addWidget(self.repo_status)
        self.repo_progress = QProgressBar()
        self.repo_progress.setRange(0, 0)
        self.repo_progress.hide()
        repo_layout.addWidget(self.repo_progress)
        self.repo_result = QTextBrowser()
        self.repo_result.setOpenExternalLinks(True)
        repo_layout.addWidget(self.repo_result, 1)
        self.tabs.addTab(self.overview, "")
        self.tabs.addTab(self.activity_list, "")
        self.tabs.addTab(self.repositories_list, "")
        self.tabs.addTab(self.repo_stats, "")
        main.addWidget(self.tabs, 1)

    def _translate(self):
        self.title.setText(self.t("title"))
        self.subtitle.setText(self.t("subtitle"))
        self.username.setPlaceholderText(self.t("placeholder"))
        self.button.setText(self.t("load"))
        self.repo_reference.setPlaceholderText(self.t("repo_placeholder"))
        self.repo_button.setText(self.t("check_repo"))
        if not self.repo_progress.isVisible():
            self.repo_status.setText(self.t("repo_ready"))
        if not self.progress.isVisible():
            self.status.setText(self.t("ready") if self.data is None else f"{self.t('updated')}: {self.data['fetched_at']}")
        for card, key in zip(self.cards, ("events", "pushes", "repos", "followers")):
            card.label.setText(self.t(key))
        self.tabs.setTabText(0, self.t("overview"))
        self.tabs.setTabText(1, self.t("activity"))
        self.tabs.setTabText(2, self.t("repositories"))
        self.tabs.setTabText(3, self.t("repo_stats"))
        if self.data:
            self.show_data(self.data)
        if self.repo_data:
            self.show_repository(self.repo_data)

    def change_language(self):
        self.lang = self.language.currentData()
        self._translate()

    def start_load(self):
        username = self.username.text().strip()
        if not username:
            QMessageBox.warning(self, self.t("title"), self.t("placeholder"))
            return
        self.button.setEnabled(False)
        self.progress.show()
        self.status.setText(self.t("loading"))
        self.thread = QThread(self)
        self.loader = Loader(username)
        self.loader.moveToThread(self.thread)
        self.thread.started.connect(self.loader.run)
        self.loader.finished.connect(self.show_data)
        self.loader.failed.connect(self.show_error)
        self.loader.finished.connect(self.thread.quit)
        self.loader.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def show_error(self, message):
        self.button.setEnabled(True)
        self.progress.hide()
        self.status.setText(self.t("load_error"))
        QMessageBox.critical(self, self.t("error_title"), message)

    def start_repo_load(self):
        reference = self.repo_reference.text().strip()
        if not reference:
            QMessageBox.warning(self, self.t("repo_stats"), self.t("repo_placeholder"))
            return
        self.repo_button.setEnabled(False)
        self.repo_progress.show()
        self.repo_status.setText(self.t("repo_loading"))
        self.repo_thread = QThread(self)
        self.repo_loader = RepositoryLoader(reference)
        self.repo_loader.moveToThread(self.repo_thread)
        self.repo_thread.started.connect(self.repo_loader.run)
        self.repo_loader.finished.connect(self.show_repository)
        self.repo_loader.failed.connect(self.show_repo_error)
        self.repo_loader.finished.connect(self.repo_thread.quit)
        self.repo_loader.failed.connect(self.repo_thread.quit)
        self.repo_thread.finished.connect(self.repo_thread.deleteLater)
        self.repo_thread.start()

    def show_repo_error(self, message):
        self.repo_button.setEnabled(True)
        self.repo_progress.hide()
        self.repo_status.setText(self.t("load_error"))
        QMessageBox.critical(self, self.t("error_title"), message)

    def show_repository(self, data):
        self.repo_data = data
        repo = data["repo"]
        languages = sorted(data["languages"].items(), key=lambda pair: pair[1], reverse=True)
        self.repo_button.setEnabled(True)
        self.repo_progress.hide()
        self.repo_status.setText(repo.get("full_name", ""))
        language_html = "".join(f"<li><b>{name}</b> — {amount:,} {self.t('bytes')}</li>" for name, amount in languages)
        language_html = language_html or f"<li>{self.t('repo_no_languages')}</li>"
        self.repo_result.setHtml(
            f"<h2>{repo.get('full_name', '')}</h2>"
            f"<p><a href='{repo.get('html_url', '')}'>{repo.get('html_url', '')}</a></p>"
            f"<h3>{self.t('description')}</h3><p>{repo.get('description') or self.t('repo_no_description')}</p>"
            f"<hr><h3>{self.t('repo_profile')}</h3>"
            f"<p><b>{self.t('stars')}:</b> {repo.get('stargazers_count', 0):,} &nbsp; • &nbsp; "
            f"<b>{self.t('forks')}:</b> {repo.get('forks_count', 0):,} &nbsp; • &nbsp; "
            f"<b>{self.t('watchers')}:</b> {repo.get('watchers_count', 0):,} &nbsp; • &nbsp; "
            f"<b>{self.t('issues')}:</b> {repo.get('open_issues_count', 0):,}</p>"
            f"<p><b>{self.t('primary_language')}:</b> {repo.get('language') or '—'}</p>"
            f"<h3>{self.t('repo_languages')}</h3><ul>{language_html}</ul>"
        )

    def localized_event(self, event):
        if self.lang == "en":
            return event_text(event)
        repo = event.get("repo", {}).get("name", "repository")
        kind = event.get("type", "").replace("Event", "")
        names = {"Push": "Надіслав(ла) коміти до", "Issues": "Оновив(ла) issue у", "PullRequest": "Оновив(ла) pull request у", "Watch": "Додав(ла) зірку репозиторію", "Fork": "Форкнув(ла) репозиторій", "Create": "Створив(ла) об’єкт у", "Release": "Опублікував(ла) реліз у"}
        return f"{names.get(kind, 'Виконав(ла) дію у')} {repo}"

    def show_data(self, data):
        self.data = data
        user = data["user"]
        self.button.setEnabled(True)
        self.progress.hide()
        self.status.setText(f"{self.t('updated')}: {data['fetched_at']}")
        values = [data["contributions"], data["pushes"], user["public_repos"], user["followers"]]
        for card, value in zip(self.cards, values):
            card.number.setText(f"{value:,}")

        languages = data["languages"].most_common(10)
        max_bytes = languages[0][1] if languages else 1
        language_html = "".join(
            f"<p><b>{name}</b> — {amount:,} {self.t('bytes')}<br>"
            f"<span style='color:#1f883d'>{'━' * max(1, int(amount / max_bytes * 28))}</span></p>"
            for name, amount in languages
        ) or f"<p>{self.t('no_languages')}</p>"
        self.overview.setHtml(
            f"<h2>{user.get('name') or user['login']} <span style='color:#667085'>@{user['login']}</span></h2>"
            f"<p>{user.get('bio') or self.t('no_bio')}</p><p><a href='{user['html_url']}'>{user['html_url']}</a></p>"
            f"<hr><h3>{self.t('profile')}</h3><p>{self.t('following')}: {user['following']} &nbsp; • &nbsp; {self.t('created')}: {user.get('created_at', '')[:10]}</p>"
            f"<h3>{self.t('languages')}</h3><p style='color:#667085'>{self.t('language_hint')}</p>{language_html}"
        )
        self.activity_list.clear()
        for event in data["events"]:
            item = QListWidgetItem(f"{event.get('created_at', '')[:16].replace('T', ' ')}  ·  {self.localized_event(event)}")
            self.activity_list.addItem(item)
        if not data["events"]:
            self.activity_list.addItem(self.t("no_activity"))
        self.repositories_list.clear()
        for repo in data["repos"]:
            item = QListWidgetItem(
                f"{repo['full_name']}   {self.t('stars')}: {repo['stargazers_count']}   {self.t('forks')}: {repo['forks_count']}   [{repo.get('language') or '—'}]\n"
                f"{repo.get('description') or self.t('without_description')}"
            )
            item.setToolTip(repo.get("html_url", ""))
            self.repositories_list.addItem(item)
        if not data["repos"]:
            self.repositories_list.addItem(self.t("no_repos"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = App()
    window.show()
    sys.exit(app.exec())
