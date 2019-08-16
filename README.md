# ISARA_loader
Laser pointer tool with ISPyB integration for ISARA sample changer


Install instructions

Clone the project 
Install django for python 3 (pip3 install django)

Open views.py and update the serial port (linux is something like ttyACM0, can be found installing arduino IDE)
Check data ports on Arduino. Current is "9" for tilt and "10" for pan. Can be any, just change in views.py

python3 manage.py migrate

python3 manage.py runserver 0.0.0.0:8081
