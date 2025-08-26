@echo off
SETLOCAL

SET ENV_NAME=cq-env
SET PYTHON_CMD=python

echo Buscando Python...
where %PYTHON_CMD% >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python no esta instalado o no se encuentra en el PATH.
    echo Por favor, instala Python 3 y asegurate de que este en el PATH.
    pause
    exit /b 1
)

echo Creando entorno virtual '%ENV_NAME%'...
if not exist "%ENV_NAME%\" (
    %PYTHON_CMD% -m venv %ENV_NAME%
) else (
    echo El entorno virtual '%ENV_NAME%' ya existe.
)

echo Instalando dependencias desde requirements.txt...
call "%ENV_NAME%\Scripts\pip.exe" install -r requirements.txt

echo.
echo --------------------------------------------------
echo ^!Instalacion completada!
echo.
echo Para activar el entorno virtual, ejecuta en tu terminal:
echo %ENV_NAME%\Scripts\activate
echo --------------------------------------------------
pause