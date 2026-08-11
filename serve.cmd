@echo off
cd /d "%~dp0"
echo Open http://localhost:8000/
echo index.html is standalone — file:// also works (Ctrl+F5 if you see a cached page).
python -m http.server 8000
