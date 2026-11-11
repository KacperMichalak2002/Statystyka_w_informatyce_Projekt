@echo off
cd /d "%~dp0.."

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; sys.exit(sys.version_info < (3, 12))" 2>nul || (
        echo Srodowisko .venv ma za stara wersje Pythona - tworze je od nowa.
        rmdir /s /q ".venv"
    )
)

if exist ".venv\Scripts\python.exe" goto :check_installed_requirements

echo Tworze srodowisko .venv (tylko za pierwszym razem)...
for %%v in (3.14 3.13 3.12) do (
    if not exist ".venv\Scripts\python.exe" py -%%v -m venv .venv 2>nul
)
if not exist ".venv\Scripts\python.exe" python -m venv .venv 2>nul
if not exist ".venv\Scripts\python.exe" goto :python_missing

".venv\Scripts\python.exe" -c "import sys; sys.exit(sys.version_info < (3, 12))" || goto :python_too_old

:check_installed_requirements
if exist ".venv\installed_requirements.txt" (
    fc /b "requirements.txt" ".venv\installed_requirements.txt" >nul && ".venv\Scripts\python.exe" -c "import football_stats" 2>nul && exit /b 0
)

echo Instaluje biblioteki (moze to potrwac kilka minut)...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo Instalacja bibliotek nie powiodla sie. Sprawdz polaczenie z internetem i uruchom ponownie.
    exit /b 1
)
copy /y "requirements.txt" ".venv\installed_requirements.txt" >nul
echo Biblioteki zainstalowane.
exit /b 0

:python_too_old
rmdir /s /q ".venv"
echo Znaleziony Python jest za stary. Projekt wymaga Pythona 3.12 lub nowszego.
echo Zainstaluj nowsza wersje ze strony python.org i uruchom ponownie.
exit /b 1

:python_missing
echo Nie znaleziono Pythona. Zainstaluj Pythona 3.12 lub nowszego ze strony python.org
echo i podczas instalacji zaznacz opcje "Add python.exe to PATH".
exit /b 1
