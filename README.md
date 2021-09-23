# Web App for Chemical Engineering Fundamentals
Visualisation of chemical engineering concepts such as theormodynamics and reactor residence time distribution through web-based applications

## How to Preview HTML
Step 1) Clone Repository (Github Desktop), else download zip  
Step 2) Open in VSCode and in terminal, install dependencies by running "pip install - r requirements.txt"  
Step 3) Go to main.py and run code  
Step 4) Wait for the code to finish running and ctrl+click the server which should prompt on the terminal when done  

## In Progress
1) Minor UI edits

## Remarks
Components is just a dummy folder with prior references and calculations.  
The actual ones are:  
1) main.py - controls the manipulation of variables to be rendered  
2) VLECalculations.py - handles the VLE calculations at set params [n,T,P,comp,z]  
3) plot.py - in charge of plotting the various graphs  
4) RTD.py - Ideal RTD calculations 
5) Real_RTD.py - Real_RTD calculations (Bypass & Dead Vol)
6) static - in charge of animations  
7) Templates - individual HTML pages




