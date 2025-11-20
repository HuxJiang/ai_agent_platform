@echo off

call "%~dp0load_env.bat" || exit /b 1

set "REMOTE_NAME=origin"
set "UPSTREAM_NAME=upstream"

echo Syncing with upstream...
echo Upstream: %UPSTREAM_REPO_URL% (%UPSTREAM_BRANCH_NAME%)
echo My Repo: %MY_REPO_URL% (%MY_BRANCH_NAME%)

:: Check and setup upstream remote
git remote get-url %UPSTREAM_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    git remote add %UPSTREAM_NAME% %UPSTREAM_REPO_URL%
)

:: Fetch from upstream
git fetch %UPSTREAM_NAME%
if %errorlevel% neq 0 (
    echo Error: Fetch from upstream failed
    pause
    exit /b 1
)

:: Switch to branch and merge
git checkout %MY_BRANCH_NAME%
git merge %UPSTREAM_NAME%/%UPSTREAM_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo Error: Merge conflict
    git merge --abort >nul 2>&1
    pause
    exit /b 1
)

:: Push to my remote
git push %REMOTE_NAME% %MY_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo Error: Push failed
    pause
    exit /b 1
)

echo Success: Synced with upstream
pause