@echo off
echo Preparando datos para Power BI...
cd /d "%~dp0.."
python scripts\powerbi_prep.py
echo.
echo Si no hay errores, los datos estan listos para usar en Power BI.
echo Abre el archivo tableau\Analisis_Netflix.pbix para ver el dashboard.
pause
