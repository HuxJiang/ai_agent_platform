@echo off

call "%~dp0load_env.bat" || exit /b 1

set "GITHUB_PR_URL=https://github.com/HuxJiang/ai_agent_platform/compare/%UPSTREAM_BRANCH_NAME%...yangyuchen123:%MY_BRANCH_NAME%?expand=1"

echo Opening PR page...
start "" "%GITHUB_PR_URL%"

echo PR page opened in browser
pause