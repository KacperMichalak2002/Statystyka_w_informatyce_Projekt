@echo off
cd /d "%~dp0"
call "%~dp0scripts\setup_environment.bat" || goto :failure

echo Uruchamiam aplikacje. Zamknij to okno albo nacisnij Ctrl+C, aby ja zatrzymac.
".venv\Scripts\python.exe" -m streamlit run app.py
goto :end

:failure
echo.
echo Cos poszlo nie tak - przeczytaj komunikat powyzej.

:end
pause
