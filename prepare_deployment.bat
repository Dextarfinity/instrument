@echo off
echo ========================================
echo Preparing Cloud Deployment Package
echo ========================================
echo.

cd ..

echo Checking for trained model file...
if exist "best.pt" (
    echo ✓ Found best.pt
    echo.
    echo Copying to cloud_deployment folder...
    copy "best.pt" "cloud_deployment\best.pt"
    
    if exist "cloud_deployment\best.pt" (
        echo ✓ Model copied successfully!
        dir "cloud_deployment\best.pt"
    ) else (
        echo ✗ Failed to copy model file
        pause
        exit /b 1
    )
) else (
    echo ✗ best.pt not found in root directory
    echo.
    echo Please ensure your trained model (best.pt) exists in:
    echo %CD%
    pause
    exit /b 1
)

echo.
echo ========================================
echo Checking cloud_deployment files...
echo ========================================
cd cloud_deployment

echo.
echo Required files:
if exist "main.py" (echo ✓ main.py) else (echo ✗ main.py MISSING)
if exist "requirements.txt" (echo ✓ requirements.txt) else (echo ✗ requirements.txt MISSING)
if exist "Procfile" (echo ✓ Procfile) else (echo ✗ Procfile MISSING)
if exist "railway.json" (echo ✓ railway.json) else (echo ✗ railway.json MISSING)
if exist "best.pt" (echo ✓ best.pt ^(YOUR MODEL^)) else (echo ✗ best.pt MISSING)
if exist "README.md" (echo ✓ README.md) else (echo ✗ README.md MISSING)

echo.
echo ========================================
echo Cloud Deployment Package Ready!
echo ========================================
echo.
echo Next steps:
echo 1. Upload this cloud_deployment folder to GitHub
echo 2. Connect Railway to your GitHub repository
echo 3. Railway will automatically deploy
echo.
echo OR use Railway CLI:
echo   railway login
echo   railway init
echo   railway up
echo.
echo Your model detects these instruments:
echo   agung, bangsi, chimes, dabakan, dlesung, 
echo   gabbang, gandang, gangsa, gimbal, kalatong, kulintang
echo.
pause
