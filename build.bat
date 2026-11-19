@echo off
setlocal

rem ==== Переход в папку скрипта ====
cd /d "%~dp0"

echo ============================================
echo  Building MatrixLib.dll
echo ============================================

rem ==== Компиляция ====
g++ -shared -O2 -std=c++17 -Wall -Wextra ^
    -static-libgcc -static-libstdc++ ^
    -o MatrixLib.dll Matrix.cpp MatrixWrapper.cpp

if errorlevel 1 (
    echo.
    echo [FAIL] Compilation failed.
    exit /b 1
)

echo [OK] Compilation succeeded.

rem ==== Проверка: файл создан ====
if not exist MatrixLib.dll (
    echo [FAIL] MatrixLib.dll not found.
    exit /b 1
)
echo [OK] MatrixLib.dll exists.

for %%F in (MatrixLib.dll) do set DLL_SIZE=%%~zF
echo      Size: %DLL_SIZE% bytes

rem ==== Проверка: экспортированные символы ====
echo.
echo ============================================
echo  Checking exports
echo ============================================

set EXPORT_COUNT=0
set REQUIRED_EXPORTS=matrix_create matrix_destroy matrix_clone matrix_rows matrix_cols matrix_get_element matrix_set_element matrix_copy_from matrix_copy_to matrix_add matrix_multiply matrix_add_assign matrix_to_string matrix_last_error

for %%F in (%REQUIRED_EXPORTS%) do (
    objdump -p MatrixLib.dll 2>nul | findstr /C:"%%F" >nul
    if errorlevel 1 (
        echo [MISSING] %%F
    ) else (
        echo [FOUND]   %%F
    )
)

rem ==== Итог ====
echo.
echo ============================================
echo  Build finished. MatrixLib.dll ready.
echo ============================================

endlocal