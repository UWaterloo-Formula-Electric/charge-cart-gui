# README #

DemoGeneratedGUI is the file that generated by Qt designer. 
As the same says, it is a demo such as constructor 
We need to manually add a construct so it is not static class and therefore can be called from child class

untitled.ui is the file from Qt desinger

# Warning
Following is the command to get python file from .ui file
python3 -m PyQt6.uic.pyuic -o testing1.py -x untitled.ui
The command will overwrite all the current code so don't touch the file except for adding a constructor
 

 # TODO
 1.MiniBatch dictioanry into 5 dictionary doesn't seem to be a good idea
    - maybe use for loop instead like for i in range(5)

2. Send setting current requeset
3. Send balancing pack request
4. Graph current and voltage
5. Add extra tables for temperature for 70 cells
6. Raw voltqage/pack current
7. State of charge
