# Agroscope TillerCounter

Basic counting tool for winter wheat tillers based on hand-collected bundle samples. Automatic detection via Hough transform. Corrections are possible via human labeler.

## Required software

- Ubuntu 20.04
- Python 3.8 or higher
- Packages: opencv-python, numpy, pillow (installed via pip)

## Basic usage
Clone repository: <br>
``git clone git@github.com:agroscope-ch/TillerCounterGui.git``

Run Tiller Counter from your python installation and environment (required packages given previously). <br>
``python src/TillerCounterGui.py``

The current configuration (config.py) is optimized for two screens, where the TillerCounter GUI is displayed in the right screen. 
If needed, adjust window size and display confiuration by changing the config.py file. Set USE_TWO_SCREENS = False if used with a single screen or if the TillerCounter GUI should be displayed on left screen.