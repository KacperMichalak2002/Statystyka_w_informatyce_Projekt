@echo off
cd /d "%~dp0"
call "%~dp0setup_environment.bat" || goto :failure

if not exist "app.py" (
    echo Plik app.py jeszcze nie istnieje - aplikacja powstanie w kolejnych etapach.
    goto :end
)

echo Uruchamiam aplikacje. Zamknij to okno albo nacisnij Ctrl+C, aby ja zatrzymac.
".venv\Scripts\python.exe" -m streamlit run app.py
goto :end

:failure
echo.
echo Cos poszlo nie tak - przeczytaj komunikat powyzej.

:end
pause
