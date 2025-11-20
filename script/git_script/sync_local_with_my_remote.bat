@echo off

call "%~dp0load_env.bat" || exit /b 1

set "REMOTE_NAME=origin"

echo Syncing local with remote...
echo Branch: %MY_BRANCH_NAME%
echo Remote: %REMOTE_NAME%

git fetch %REMOTE_NAME%
if %errorlevel% neq 0 (
    echo Error: git fetch failed
    pause
    exit /b 1
)

git checkout %MY_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo Error: Cannot switch to branch %MY_BRANCH_NAME%
    pause
    exit /b 1
)

git pull %REMOTE_NAME% %MY_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo Error: git pull failed
    pause
    exit /b 1
)

echo Success: Synced with %REMOTE_NAME%/%MY_BRANCH_NAME%
pause