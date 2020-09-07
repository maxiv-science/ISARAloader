# ISARA loader
BioMAX beamline sample location and experiment planner

Web application to locate available positions in the BioMAX sample changer and prepare the session in ISPyB for MXCuBE3.

Uses [RpiMotorLib](https://github.com/gavinlyonsrepo/RpiMotorLib) for Servo motor functions
Uses [ISPyB](https://github.com/ispyb/ISPyB) for beamline database information

It is designed to run from a Raspberry Pi 3 

## Application map

- Read information from BioMAX ISARA tango device
- Checks user proposals from ISPyB and shipment contents
- Assign position in ISARA and saves the information back in ISPyB
- Provide staff access for remote data collection preparation



## Development

### Components

The ISARA_loader consists of 3 major components:

 * Web Application
 * ISPyB API
 * Servo motor functions

The _Web Application_ component implements the UI part of the ISARA_loader.
It is build on top of Django framework, and serves the web-requests.

The _ISPyB API_ component handles database read/write.
User access is grated by MAXIV's Digital User Office

The _Servo motor functions_ are used to control PWM cycles of two orthogonal servo SG90 motors.

### Dependencies

The required python package are listed in both `environment.yml`.

### Set-up with conda

Follow steps below to set-up an environments for running ISARA_loader using conda.

- use you prefered method for installing [conda](https://docs.conda.io/en/latest/)
- clone this repository

    git clone <repo-url> <src-dir>

- create conda environment 'ISARAloader'

    conda env create -f <src-dir>/environment.yml

The conda environment 'ISARAloader' will contain all required package for ISARAloader webapp.

### Running the Webapp

To run ISARAloader application the _Web Application_ component must be started.

To start _Web Application_ activate 'ISARAloader' environment and run:

    ./manage.py runserver 0.0.0.0:<port>
    
Access it from any device connected to the same network. The intented access is from a touchscreen device, such as a Tablet.

### Training the laser positions

Open the terminal and SSH to the Raspberry Pi:


python3 /home/pi/ISARA_loader/laser/views/calibration.py


Your terminal will capture keyboard inputs and move the laser in pan-tilt

Shortcuts
| Keyboard shortcut  | Action |
| ------------- | ------------- |
| arrow up	| Move 1 degree up |
| keypad 8	| Move 0.1 degree up |
| arrow down	| Move 1 degree down |
| keypad 2	| Move 0.1 degree down |
| arrow right	| Move 1 degree right |
| keypad 6	| Move 0.1 degree right |
| arrow left	| Move 1 degree left |
| keypad 4	| Move 0.1 degree left |
| n	| Next basket |
| p	| Previous basket |
| s	| Save all baskets definitions  |
| spacebar	| Move laser to stored position for current basket  |
| r	| Reset angles for the current basket to [90,90]  |
| ESC	| Quits the program  |

One or more positions can be updated at any time. 

After the definitions are updated, go the iPad, click Settings -> Update Definitions. This will load new values from previously save definition files.

If you need to reset all angular definitions at once, delete the file:

/home/pi/baskets.pickle

Start the calibration again and proceed as described before.

