@echo off

:: Load environment variables
call "%~dp0load_env.bat" || exit /b 1

:: Set remote repository
set "REMOTE=origin"

:: Get commit message
set /p "commit_msg=Enter commit message: "

:: Commit changes
git add .
git commit -m "%commit_msg%"

:: Push to remote
git push %REMOTE% %MY_BRANCH_NAME%

echo Code pushed to %REMOTE%/%MY_BRANCH_NAME%
pause