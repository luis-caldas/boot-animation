#!/usr/bin/env python

# Defaults
DEFAULT_THEME="main"

# Output
DISTRIBUTE="dist"

############
# Plymouth #
############

# Paths
PLYMOUT_FOLDER="plymouth"

# Replacing
FIND_CHAR = '%'
REPLACE = {
    "PASS_MSG": "Authenticate",
    "BULLET_CHAR": '◊'
}

###########
# Android #
###########

# Paths
ANDROID_FOLDER="android"

# Building
REFRESH_RATE = 60

# Paths
FOLDER_NAME = "part0"
DESCRIPTION_FILE = "desc.txt"
OUTPUT_NAME = "bootanimation.zip"

# Resolutions
RESOLUTIONS = {
    "alioth": [1080, 2400],
    "beryllium": [1080, 2246],
    "skipjack": [360, 360]
}
