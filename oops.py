import os

textFileToRun = "oops.txt"
with open(textFileToRun) as f:
    for line in f:
        if(line != "\n"):
            line = 'cmd /c ' + line
            # print("line", line)
            os.system(line)