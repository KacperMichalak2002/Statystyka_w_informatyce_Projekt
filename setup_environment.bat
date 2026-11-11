@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto :check_installed_requirements

echo Tworze srodowisko .venv (tylko za pierwszym razem)...
py -3.14 -m venv .venv 2>nul || py -3 -m venv .venv 2>nul || python -m venv .venv
if not exist ".venv\Scripts\python.exe" (
    echo Nie znaleziono Pythona. Zainstaluj Pythona 3.10 lub nowszego ze strony python.org.
    exit /b 1
)

:check_installed_requirements
if exist ".venv\installed_requirements.txt" (
    fc /b "requirements.txt" ".venv\installed_requirements.txt" >nul && exit /b 0
)

echo Instaluje biblioteki (moze to potrwac kilka minut)...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo Instalacja bibliotek nie powiodla sie.
    exit /b 1
)
copy /y "requirements.txt" ".venv\installed_requirements.txt" >nul
echo Biblioteki zainstalowane.
exit /b 0
