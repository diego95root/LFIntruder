
import os, argparse

def generatePaths(Max = None):
    paths = []
    root = os.path.abspath(os.sep)
    for previous, dirs, files in os.walk(root):
        for dir in dirs: 
            if len(paths) == Max:
                return paths
            paths.append(os.path.join(previous, dir))
    return paths

def savePaths(outfile, pathList):
    with open(outfile, "wa") as file:
        for i in paths:
            file.write(i+"\n")
        file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="paths.txt", type=str, help="Write generated paths to file")
    parser.add_argument("-n", "--number", default=500, type=int, help="Number of maximum paths to be generated")
    parser.add_argument("-s", "--string", default="", type=str, help="Filename to be searched")
    args = parser.parse_args()

    outfile  = args.__dict__["file"]
    maxPaths = args.__dict__["number"]
    file_str = args.__dict__["string"]

    paths = generatePaths(maxPaths)
    savePaths(outfile, paths)

