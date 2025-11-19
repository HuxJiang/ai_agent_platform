@echo off

:: Check .env file
if not exist ".env" (
    echo Error: .env file not found
    exit /b 1
)

:: Load environment variables
for /f "usebackq tokens=1* delims==" %%A in (".env") do (
    if not "%%A"=="" set "%%A=%%B"
)

:: Validate required variables
if "%MY_BRANCH_NAME%"=="" (
    echo Error: MY_BRANCH_NAME not set
    exit /b 1
)