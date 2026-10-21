@echo off
REM Chạy giao diện web của chatbot: mở http://localhost:8501
chcp 65001 >nul
cd /d "%~dp0"
".venv\Scripts\python.exe" -m streamlit run app.py
pause
