@echo off
REM Script de lancement automatique du pipeline
REM Ce script peut être appelé par le Task Scheduler

echo ================================================
echo    PIPELINE DE VEILLE CONCURRENTIELLE
echo ================================================
echo.

REM Enregistrer la date et l'heure de démarrage
echo Demarrage : %date% %time%
echo.

REM Se placer dans le bon dossier
cd /d %~dp0

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier que l'activation a réussi
if errorlevel 1 (
    echo ERREUR: Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

echo Environnement virtuel active.
echo.

REM Lancer le pipeline
echo Lancement du pipeline...
python main.py

REM Capturer le code de sortie
set EXIT_CODE=%errorlevel%

echo.
echo ================================================
if %EXIT_CODE% equ 0 (
    echo SUCCES: Pipeline termine avec succes
) else (
    echo ERREUR: Le pipeline a rencontre des erreurs
)
echo ================================================
echo Fin : %date% %time%
echo.

REM Si exécuté manuellement, pause pour voir les résultats
REM (le Task Scheduler ignorera cette ligne)
if "%1"=="manual" pause

exit /b %EXIT_CODE%