if not "%1"=="am_admin" (
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList 'am_admin'"
    exit /b
)

cd %USERPROFILE%\Desktop\FRC2022
set activatePath=%USERPROFILE%\miniconda3\Scripts\activate.bat
set minicondaPath=%USERPROFILE%\miniconda3
call %activatePath% %minicondaPath%
call conda activate frc2022
python utils\autostartsetup.py
pause