@echo off
setlocal EnableExtensions EnableDelayedExpansion
cls

:: --------------------------------------------------------
::
:: HOW TO USE:
:: To use this .bat file for running and updating Sparkle-
:: Neuroscience-Converter, make a copy of this file and rename it
:: something easy to remember (e.g. SparkleNeuroscience.bat).
:: Now in the copy of this file you will want to change the
:: variable of "location" (line 24) with the path to the
:: Sparkle-Neuroscience-Converter directory (where you found this file).
:: After you complete that you will want to change the
:: variable for "gitLocation" (line 28) with the path to
:: where your git.exe is stored. Once you have those set,
:: you can either create a shortcut to your newly edited
:: file or just run the .bat file. While running it with
:: this code, it will check for updates before running
:: and will ask the user if they wish to update if there
:: are any new updates.
::
:: Place your path to Sparkle-Neuroscience-Converter here
set location="C:\Users\Name\Documents\Sparkle-Neuroscience-Converter\"
cd %location%
::
:: Place your path to Git here
set gitLocation="C:\Program Files (x86)\Git\bin"
SET PATH=%PATH%;%gitLocation%
::
:: --------------------------------------------------------

title Sparkle-Neuroscience-Converter

:: Get versions of Sparkle-Neuroscience-Converter
git remote update
for /f "delims=" %%i in ('git rev-parse @{0}') do set local=%%i
for /f "delims=" %%i in ('git rev-parse origin/master') do set remote=%%i
for /f "delims=" %%i in ('git merge-base @ origin/master') do set base=%%i

echo.

:: Check relation of various versions
if "%local%" equ "%remote%" (
    echo Sparkle-Neuroscience-Converter is up to date.
    goto :runSparkleNeuroscience
) else if "%local%" equ "%base%" (
    echo A newer version of Sparkle-Neuroscience-Converter is avaliable.
) else if "%remote%" equ "%base%" (
    echo Your local branch of Sparkle-Neuroscience-Converter is ahead of origin/master.
    goto :runSparkleNeuroscience
)

set "answer=%globalparam1%"
goto :answerCheck

:updatePrompt
set /p "answer=Update Sparkle-Neuroscience-Converter? (y or n): "
goto :answerCheck

:answerCheck
if not defined answer goto :updatePrompt

echo.

if "%answer%" == "y" (
    git pull
)

:runSparkleNeuroscience
echo.
python run.py