@echo off
cd..
echo Activating Virtural environment...
call .\venv\Scripts\activate

echo upgrading pip...
python -m pip install --upgrade pip


echo Installing pipreqs...
pip install pipreqs

echo Export to requirements.txt
pipreqs . --force --encoding utf-8

pause