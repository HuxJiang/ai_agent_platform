@echo off
:: 设置UTF-8编码以正确显示中文

setlocal

:: 加载环境变量
call "%~dp0load_env.bat" || exit /b 1

:: 设置远程仓库名称，默认使用origin
set "REMOTE_NAME=origin"

:: 显示同步信息
echo 正在同步本地仓库与远程仓库...
echo 本地分支：%MY_BRANCH_NAME%
echo 远程仓库：%REMOTE_NAME%

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

:: 从远程仓库获取最新代码
echo 从远程仓库获取最新代码...
git fetch %REMOTE_NAME%
if %errorlevel% neq 0 (
    echo 错误：git fetch 命令执行失败，请检查网络连接和远程仓库配置
    pause
    exit /b 1
)

:: 切换到指定分支
echo 切换到分支 %MY_BRANCH_NAME%...
git checkout %MY_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo 错误：无法切换到分支 %MY_BRANCH_NAME%，请检查分支是否存在
    pause
    exit /b 1
)

:: 从远程仓库拉取最新代码到本地
echo 从远程仓库拉取最新代码...
git pull %REMOTE_NAME% %MY_BRANCH_NAME%
if %errorlevel% neq 0 (
    echo 错误：git pull 命令执行失败，可能存在合并冲突
    pause
    exit /b 1
)

echo 成功：本地仓库已与远程仓库 %REMOTE_NAME%/%MY_BRANCH_NAME% 同步完成！
endlocal
pause