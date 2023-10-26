# This script may be necessary if you are working with google drive folders. Google drive creates .ini configuration files that may need to be deleted for the workflow to work.
import os

ini_list = []

for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith(".ini"):
            ini_list.append(os.path.join(root, file))

print(ini_list)

for file in ini_list:
    os.remove(file)


