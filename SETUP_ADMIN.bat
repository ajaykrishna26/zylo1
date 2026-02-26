@echo off
REM Admin Setup Script - Double-click to run
REM This script creates the admin account in MongoDB

cd /d "C:\Users\DELL\OneDrive\Pictures\Desktop\reading_assistant-ak\reading_assistant-ak"

echo.
echo ========================================
echo ADMIN ACCOUNT SETUP
echo ========================================
echo.
echo Creating admin account:
echo   Email: admin@gmail.com
echo   Password: Admin@123
echo.

python quick_admin.py

echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo You can now log in at:
echo   http://localhost:3002
echo.
echo Credentials:
echo   Email: admin@gmail.com
echo   Password: Admin@123
echo.
pause
