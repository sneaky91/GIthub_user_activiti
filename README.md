# GitHub User Activity

Приложение показывает профиль GitHub, недавнюю активность, репозитории и языки программирования.

Во вкладке **Repository Stats** можно вставить ссылку на репозиторий GitHub или формат `owner/repository`. Она показывает описание, stars, forks, watchers, открытые issues, основную и все используемые языки.

В проекте есть две версии:

- `gui.py` — современный GUI на PySide6 (Qt);
- `cli.py` — версия для командной строки.

Приложение использует публичный GitHub REST API и обычно не требует токена.

## Установка на Windows

### 1. Установите Python

Ошибка `python : The term 'python' is not recognized...` означает, что Python ещё не установлен или не добавлен в PATH. Скачайте Python 3.10 или новее с [официального сайта](https://www.python.org/downloads/windows/).

В установщике обязательно включите:

- **Add Python to PATH**;
- **pip**;
- **Python Launcher**.

После установки полностью закройте и заново откройте PowerShell.

### 2. Проверьте Python и pip

Откройте PowerShell в папке проекта и проверьте Python:

```powershell
python --version
python -m pip --version
```

Если команда `python` не работает, попробуйте launcher:

```powershell
py --version
py -m pip --version
```

Если работают команды с `py`, используйте `py` вместо `python` во всех следующих командах.

### 3. Если pip отсутствует

Если Python работает, но `pip` не найден, восстановите его встроенной командой:

```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

Для launcher Windows:

```powershell
py -m ensurepip --upgrade
py -m pip install --upgrade pip
```

### 4. Установите зависимости проекта

```powershell
python -m pip install -r requirements.txt
```

Или, если используется launcher:

```powershell
py -m pip install -r requirements.txt
```

### Запуск кнопкой Run в VS Code

VS Code может использовать другой Python-интерпретатор, не тот, в который устанавливались пакеты. Если появляется ошибка `ModuleNotFoundError: No module named 'PySide6'`, установите зависимости через тот же интерпретатор:

```powershell
python -m pip install -r requirements.txt
```

После этого в VS Code нажмите `Ctrl+Shift+P` → **Python: Select Interpreter** и выберите Python, в котором установлены зависимости. Обычно это Python 3.13 или 3.12, а не `Microsoft\WindowsApps\python.exe` alias.

## Запуск из исходников

```powershell
python gui.py
python cli.py kamranahmedse
```

Для увеличения лимита GitHub API можно указать токен:

```powershell
$env:GITHUB_TOKEN = "ваш_токен"
```

## Сборка EXE и ZIP

В `requirements.txt` уже находятся и PySide6, и PyInstaller, поэтому отдельная установка PyInstaller не нужна:

```powershell
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

После сборки появятся:

- `dist\github-user-activity-gui.exe`;
- `dist\github-user-activity-cli.exe`;
- `github-user-activity.zip` — архив с обеими версиями и README.

Примечание: публичный REST API отдаёт до 100 недавних events. Поэтому `contributions` в приложении — это количество загруженных недавних событий, а не полный contribution graph GitHub за год.
