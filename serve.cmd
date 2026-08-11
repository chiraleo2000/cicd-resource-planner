@echo off
cd /d "%~dp0"
echo Open http://localhost:8000/
echo For file:// use planner-standalone.html instead.
python -m http.server 8000
