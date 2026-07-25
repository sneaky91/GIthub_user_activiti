$ErrorActionPreference = "Stop"
if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m pip install -r requirements.txt
    python -m PyInstaller --clean --onefile --windowed --name github-user-activity-gui gui.py
    python -m PyInstaller --clean --onefile --console --name github-user-activity-cli cli.py
    Compress-Archive -Path "dist\github-user-activity-gui.exe", "dist\github-user-activity-cli.exe", "README.md" -DestinationPath "github-user-activity.zip" -Force
    Write-Host "Created github-user-activity.zip"
} else {
    Write-Host "PyInstaller не найден. Установите его командой: python -m pip install pyinstaller"
    exit 1
}
