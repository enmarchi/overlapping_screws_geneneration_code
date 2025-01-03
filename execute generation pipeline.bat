@echo off
set num_trials=100
set count=0

:loop
if %count% geq %num_trials% goto end

echo ****************************************
echo Starting interation %count% of %num_trials%.
echo ****************************************

"path to the command  \blenderproc" run ^
    "path to \code\generate synthetic image.py" ^
    "path to the directory containing this script" || echo Iteration %count% failed, continue...

echo Iteration %count% completed.
echo Iteration %count% completed.

set /a count+=1
goto loop

:end
echo ****************************************
echo Script completed.
echo ****************************************
pause
