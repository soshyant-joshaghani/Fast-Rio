@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "CTRL_NAME=fast-rio-ctrl"
set "PY_EXE="
set "PY_ARGS="

REM Prefer py launcher - bare python is often the Windows Store stub.
call :find_python
if defined PY_EXE goto :have_python

echo [%CTRL_NAME%] Python 3.10+ not found. Installing Python 3.12 via winget...
where winget >nul 2>&1
if errorlevel 1 (
  echo [%CTRL_NAME%] winget not found. Install Python from https://www.python.org/ or enable App Installer.
  pause
  exit /b 1
)
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  echo [%CTRL_NAME%] winget failed to install Python.Python.3.12
  pause
  exit /b 1
)
call :refresh_path
call :find_python
if not defined PY_EXE (
  echo [%CTRL_NAME%] Python 3.10+ still not found after install. Open a new terminal or reboot, then retry.
  pause
  exit /b 1
)

:have_python
if not exist ".venv\Scripts\python.exe" (
  echo [%CTRL_NAME%] Creating .venv and installing requirements...
  "%PY_EXE%" %PY_ARGS% -m venv .venv
  if errorlevel 1 (
    echo Failed to create .venv
    pause
    exit /b 1
  )
  ".venv\Scripts\pip.exe" install -r requirements.txt
  if errorlevel 1 (
    echo Failed to install requirements.txt
    pause
    exit /b 1
  )
)

set "CTRL_PY=.venv\Scripts\python.exe"

REM No args: interactive REPL (stays open). With args: run once.
if "%~1"=="" (
  "%CTRL_PY%" main.py
  echo.
  pause
  exit /b %ERRORLEVEL%
)

"%CTRL_PY%" main.py %*
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo Command failed with exit code %ERR%
  pause
)
exit /b %ERR%

:find_python
set "PY_EXE="
set "PY_ARGS="
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1
  if not errorlevel 1 (
    set "PY_EXE=py"
    set "PY_ARGS=-3"
    exit /b 0
  )
)
where python >nul 2>&1
if not errorlevel 1 (
  for /f "delims=" %%P in ('where python 2^>nul') do (
    echo %%P | findstr /I /C:"WindowsApps" >nul
    if errorlevel 1 (
      "%%P" -c "import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1
      if not errorlevel 1 (
        set "PY_EXE=%%P"
        set "PY_ARGS="
        exit /b 0
      )
    )
  )
)
where python3 >nul 2>&1
if not errorlevel 1 (
  for /f "delims=" %%P in ('where python3 2^>nul') do (
    "%%P" -c "import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1
    if not errorlevel 1 (
      set "PY_EXE=%%P"
      set "PY_ARGS="
      exit /b 0
    )
  )
)
exit /b 0

:refresh_path
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYSPATH=%%B"
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USERPATH=%%B"
if defined USERPATH if defined SYSPATH (
  set "PATH=!USERPATH!;!SYSPATH!"
) else if defined SYSPATH (
  set "PATH=!SYSPATH!"
) else if defined USERPATH (
  set "PATH=!USERPATH!"
)
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PATH=%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%PATH%"
if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PATH=%LocalAppData%\Programs\Python\Python313;%LocalAppData%\Programs\Python\Python313\Scripts;%PATH%"
if exist "%LocalAppData%\Programs\Python\Python314\python.exe" set "PATH=%LocalAppData%\Programs\Python\Python314;%LocalAppData%\Programs\Python\Python314\Scripts;%PATH%"
exit /b 0
