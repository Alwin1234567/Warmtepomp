@echo off
REM Activate the virtual environment
call venv\Scripts\activate

REM Generate the requirements.txt file
pip freeze > requirements.txt

REM Deactivate the virtual environment
deactivate
