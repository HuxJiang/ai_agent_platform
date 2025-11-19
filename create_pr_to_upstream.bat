@echo off
:: 设置UTF-8编码以正确显示中文

setlocal

:: 加载环境变量
call "%~dp0load_env.bat" || exit /b 1

:: 显示PR信息
echo 正在准备创建Pull Request...
echo 来源：yangyuchen123/internet_dev:%MY_BRANCH_NAME%
echo 目标：HuxJiang/ai_agent_platform:%UPSTREAM_BRANCH_NAME%

:: 构建PR URL
set "GITHUB_PR_URL=https://github.com/HuxJiang/ai_agent_platform/compare/%UPSTREAM_BRANCH_NAME%...yangyuchen123:%MY_BRANCH_NAME%?expand=1"

echo. 
echo 请确保您已将代码推送到您的远程仓库（运行push_to_my_remote.bat）
echo. 
echo 准备在浏览器中打开Pull Request创建页面...

:: 在默认浏览器中打开PR页面
start "" "%GITHUB_PR_URL%"

:: 提示用户手动完成PR创建
echo. 
echo 请在浏览器中：
echo 1. 检查PR信息是否正确
2. 填写PR标题和详细描述
3. 点击"Create pull request"按钮完成PR创建

:: 验证远程仓库的分支是否已推送
echo. 
echo 正在验证分支是否已推送...
git ls-remote --heads origin %MY_BRANCH_NAME% > nul

if %errorlevel% neq 0 (
    echo 警告：未找到远程分支 %MY_BRANCH_NAME%，请先运行push_to_my_remote.bat推送代码
) else (
    echo 确认：远程分支 %MY_BRANCH_NAME% 已存在，可以创建PR
)

echo. 
echo 请在浏览器中完成PR创建流程
endlocal
pause