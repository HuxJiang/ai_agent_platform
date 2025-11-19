@echo off
:: 设置UTF-8编码以正确显示中文

setlocal

:: 加载环境变量
call "%~dp0load_env.bat" || exit /b 1

:: 设置远程仓库名称
set "REMOTE_NAME=origin"
set "UPSTREAM_NAME=upstream"

:: 显示同步信息
echo 正在同步远程仓库与原主仓库...
echo 原主仓库：%UPSTREAM_REPO_URL% (%UPSTREAM_BRANCH_NAME%)
echo 远程仓库：%MY_REPO_URL% (%MY_BRANCH_NAME%)

:: 检查本地工作区是否有未提交的更改
echo 检查本地工作区状态...
git status --porcelain > nul
if %errorlevel% neq 0 (
    echo 警告：git status 命令执行失败，请确认当前目录是有效的Git仓库
    pause
    exit /b 1
)

:: 检查是否有未提交的更改
for /f "usebackq tokens=*" %%a in (`git status --porcelain`) do (
    if not "%%a"=="" (
        echo 错误：本地工作区有未提交的更改，请先提交或暂存这些更改
        git status
        pause
        exit /b 1
    )
)

:: 检查并添加upstream远程仓库
echo 检查upstream远程仓库配置...
git remote get-url %UPSTREAM_NAME% > nul 2>&1
if %errorlevel% neq 0 (
    echo 添加upstream远程仓库：%UPSTREAM_REPO_URL%
    git remote add %UPSTREAM_NAME% %UPSTREAM_REPO_URL%
    if %errorlevel% neq 0 (
        echo 错误：无法添加upstream远程仓库
        pause
        exit /b 1
    )
) else (
    :: 验证upstream URL是否正确
    for /f "usebackq tokens=*" %%a in (`git remote get-url %UPSTREAM_NAME%`) do (
        if not "%%a"=="%UPSTREAM_REPO_URL%" (
            echo 更新upstream远程仓库URL
            git remote set-url %UPSTREAM_NAME% %UPSTREAM_REPO_URL%
        )
    )
)

:: 从upstream获取最新代码
echo 从原主仓库获取最新代码...
git fetch %UPSTREAM_NAME%
if %errorlevel% neq 0 (
    echo 错误：无法从原主仓库获取代码，请检查网络连接
    pause
    exit /b 1
)

:: 切换到本地分支
echo 切换到本地分支 %MY_BRANCH_NAME%...
git checkout %MY_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo 错误：无法切换到分支 %MY_BRANCH_NAME%
    pause
    exit /b 1
)

:: 合并upstream代码到本地分支
echo 合并原主仓库代码到本地分支...
git merge %UPSTREAM_NAME%/%UPSTREAM_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo 错误：合并代码失败，可能存在冲突需要手动解决
    git merge --abort > nul 2>&1
    echo 已中止合并操作
    pause
    exit /b 1
)

:: 推送到用户的远程仓库
echo 推送更新到您的远程仓库...
git push %REMOTE_NAME% %MY_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo 错误：无法推送到您的远程仓库，请检查权限设置
    pause
    exit /b 1
)

echo 成功：您的远程仓库已与原主仓库同步完成！
endlocal
pause