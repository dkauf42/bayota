from datetime import datetime
import os

outputdir_toplevel = "/home/xxx/"

today = datetime.now()
if today.hour < 12:
    h = "00"
else:
    h = "12"

os.mkdir(outputdir_toplevel + today.strftime('%Y%m%d') + h)
