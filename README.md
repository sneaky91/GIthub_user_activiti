# GithubUserActivity

A Python CLI that shows a GitHub user's profile, recent public activity, and programming language statistics.

The interface uses English by default. Ukrainian is available with `--language uk`. On startup, the CLI displays an orange **Github User activity** banner in supported terminals. Colors are disabled when output is redirected or `NO_COLOR` is set.

## Getting started

### 1. Download and open the project

Download the repository as a ZIP and extract it, or clone it with Git. Open the extracted project folder — the one containing `cli.py`, `run.ps1`, and `run.sh`.

Open a terminal in that folder:

- **Windows:** open the folder in File Explorer, right-click an empty area, and choose **Open in Terminal**. Use a PowerShell tab.
- **VS Code:** open the project folder, then select **Terminal → New Terminal**.
- **Linux / macOS:** open a terminal and use `cd` to enter the project folder.

If you need to change folders manually, replace the example path with the actual location of your downloaded project:

```powershell
cd "C:\Users\YourName\Downloads\GIthubuser"
```

All commands below assume your terminal is in the project folder.

### 2. Check Python

- Python 3.10 or newer to run from source.
- An internet connection to access GitHub.
- To build an executable: a Python version supported by PyInstaller. The build scripts install PyInstaller into a local `.venv` directory.

Running from source requires no third-party packages.

Check whether Python is available:

```bash
python --version
```

On Windows, you can also try `py --version`. On Linux and macOS, try `python3 --version`. If none of these commands works, install Python and make sure it is available in your terminal. On Windows, enable **Add Python to PATH** during installation, then reopen the terminal.

If you already have the built executable, Python is not needed — see **Run the built application** below.

### 3. Find your GitHub username

Open your GitHub profile and look at its address:

```text
https://github.com/octocat
                   └── your username is this part
```

In this example, the username is **`octocat`**. Use your account's username, not your display name, email address, or full profile URL. You can also look up another user's public activity.

**Replace `YOUR_USERNAME` in the commands below with the username you want to check.** Do not type the placeholder literally. You do not need to edit any Python files.

### 4. Run with your username

**Windows / PowerShell:**

```powershell
.\run.ps1 YOUR_USERNAME
```

For example, to check the account at `https://github.com/octocat`, type:

```powershell
.\run.ps1 octocat
```

**Linux / macOS / Git Bash on Windows:**

```bash
bash run.sh YOUR_USERNAME
```

Example:

```bash
bash run.sh octocat
```

Press **Enter** and wait for the results. The app displays its banner, the user's profile, programming language statistics, and recent public activity. Language statistics may take longer because they require extra requests.

For a faster first run, skip language statistics:

```powershell
.\run.ps1 YOUR_USERNAME --no-languages
```

You can also run Python directly with `python cli.py YOUR_USERNAME`. Use `py` or `python3` instead of `python` if that is the command available on your computer.

The run scripts execute the current source code. You do not need to build the project before using them.

## Change the interface language

English is the default — no extra option is required. To use Ukrainian, add `--language uk` **after your username**:

```powershell
.\run.ps1 YOUR_USERNAME --language uk
```

In Bash:

```bash
bash run.sh YOUR_USERNAME --language uk
```

You can combine options. For example, this checks `octocat` in Ukrainian without downloading language statistics:

```powershell
.\run.ps1 octocat --language uk --no-languages
```

Use `--language en`, or leave out the language option, to return to English on the next run.

## Options

| Argument | Purpose |
| --- | --- |
| `username` | GitHub username; an optional leading `@` is accepted. |
| `--language en` | Use English, the default interface language. |
| `--language uk` | Use Ukrainian for output, API errors, event descriptions, and help text. |
| `--no-languages` | Skip programming language statistics to reduce API requests. |
| `-h`, `--help` | Show usage information. |

The interface language is selected for each run. GitHub content such as bios and issue titles stays in its original language. Standard argument parser labels and validation messages use Python's default language.

To show help in Ukrainian:

```bash
python cli.py --language uk --help
```

## Build an executable

This step is optional. Use it when you want a standalone application that runs without a separate Python installation. Run the build command from the project folder and wait for it to finish. **Do not put your GitHub username in the build command** — usernames are supplied when running the application.

PowerShell:

```powershell
.\build.ps1
```

Bash:

```bash
bash build.sh
```

On Windows, including Git Bash, the output is `dist/GithubUserActivity.exe`. On Linux and macOS, it is `dist/GithubUserActivity`. Each build targets the operating system on which it runs. The resulting executable does not require a separate Python installation.

### Run the built application

Open a terminal in the project folder and replace `YOUR_USERNAME` as before.

**Windows / PowerShell:**

```powershell
.\dist\GithubUserActivity.exe YOUR_USERNAME
.\dist\GithubUserActivity.exe YOUR_USERNAME --language uk
```

**Linux / macOS:**

```bash
./dist/GithubUserActivity YOUR_USERNAME
```

**Git Bash on Windows:**

```bash
./dist/GithubUserActivity.exe YOUR_USERNAME
```

For example: `.\dist\GithubUserActivity.exe octocat --no-languages`.

Run the executable from a terminal rather than double-clicking it: the application needs a username argument, and the terminal keeps its output visible.

## Common problems

| Problem | What to do |
| --- | --- |
| `python` is not recognized or not found | Try `py` on Windows or `python3` on Linux/macOS. If Python is not installed, install it and reopen your terminal. |
| `run.ps1`, `run.sh`, or `cli.py` cannot be found | Open the terminal in the folder containing those files. Use `dir` in PowerShell or `ls` in Bash to check. |
| The `username` argument is required | Add your GitHub username after the script or executable name, for example `.\run.ps1 octocat`. |
| The username is invalid or the user was not found | Use only the username from the profile URL. Check its spelling; do not paste the entire URL. |
| No recent public activity | The account may have no recent public events. Private activity is not shown. |
| GitHub denies requests or reports an API limit | Try again later. Use `--no-languages` to reduce requests, or configure the optional token below. |
| The executable is missing from `dist` | Run the build script first and check that it finishes successfully. |

If PowerShell reports that running scripts is disabled, use these commands for the individual script invocation:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
powershell -ExecutionPolicy Bypass -File .\run.ps1 YOUR_USERNAME
```

## Optional: GitHub token

A token is not required for a normal first run. If you already have a GitHub personal access token and want to use authenticated requests, replace `YOUR_TOKEN` with that token and `YOUR_USERNAME` with the username you want to check. The token is not your GitHub password. Keep it private; do not add it to source files or commit it to Git.

PowerShell:

```powershell
$env:GITHUB_TOKEN = "YOUR_TOKEN"
.\run.ps1 YOUR_USERNAME
```

Bash:

```bash
export GITHUB_TOKEN="YOUR_TOKEN"
bash run.sh YOUR_USERNAME
```

These commands set the token for the current terminal session. Run the application in that same terminal.

## For developers

### Project structure

- `cli.py` — command-line arguments, terminal banner, and output.
- `github_activity.py` — API requests, error handling, and event descriptions.
- `translations.py` — English and Ukrainian interface text.
- `run.ps1`, `run.sh` — run the CLI from source.
- `build.ps1`, `build.sh` — build a standalone executable.
- `requirements-build.txt` — build dependency.
- `tests/test_activity.py` — tests that run without network access.

### Tests

```bash
python -m unittest discover -s tests -v
```

## Data limits

The app requests up to 100 recent public events and displays the first 30. This is not the user's annual contribution count. Programming language totals are measured in bytes across the 30 most recently updated repositories.

If language statistics cannot be loaded, the app reports the issue and still displays the profile and activity. Profile or activity request failures return exit code `1`; invalid command-line arguments return `2`.
