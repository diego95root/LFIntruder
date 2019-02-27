
import os

def generatePaths(Max = None):
    paths = []
    root = os.path.abspath(os.sep)
    for previous, dirs, files in os.walk(root):
        for dir in dirs: 
            if len(paths) == Max:
                return paths
            paths.append(os.path.join(previous, dir))
    return paths

if __name__ == "__main__":
    paths = generatePaths(500)
    with open("paths.txt", "wa") as file:
        for i in paths:
            file.write(i+"\n")
        file.close()
