import os

ini_list = []

for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith(".ini"):
            ini_list.append(os.path.join(root, file))

print(ini_list)

for file in ini_list:
    os.remove(file)


