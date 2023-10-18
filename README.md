# README #

* DemoGeneratedGUI is the file that generated by Qt designer. 

* As the name says, it is a demo for constructor 
We need to manually add a construct in `charge_cart_GUI.py`, so it is not static class and therefore can be called from child class

```    
class Ui_MainWindow(object):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
```

* serial_parse contends all the necessary functions for communicating with the board

* charge_cart_GUI.ui is the file from Qt designer

* charge_cart_GUI.py is the generated python file from Qt designer


# Warning
Following is the command to get python file from .ui file

#### Mac
`python3 -m PyQt6.uic.pyuic -o charge_cart_GUI_testing.py -x charge_cart_GUI.ui`

#### Windows
`pyuic6 -x charge_cart_GUI.ui -o charge_cart_GUI_testing.py`

The command will overwrite all the current code in charge_cart_GUI.py 
so don't touch the file except for adding a constructor and git rid of generated "main" function
OR you know what you are doing
 

# TODO
 1.MiniBatch dictioanry into 5 dictionary doesn't seem to be a good idea
    - maybe use for loop instead like for i in range(5)
 2. Send setting current requeset
 3. Send balancing pack request
 4. Graph current and voltage
 5. Add extra tables for temperature for 70 cells
 6. Raw voltqage/pack current
 7. State of charge
