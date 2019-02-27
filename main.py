
import os, argparse, sys

def generatePaths(Max = None):
    paths = []
    root = os.path.abspath(os.sep)
    for previous, dirs, files in os.walk(root):
        for dir in dirs: 
            if len(paths) == Max:
                return paths
            paths.append(os.path.join(previous, dir))
    return paths

def generateFiles(Max = None):
    paths = []
    root = os.path.abspath(os.sep)
    for previous, dirs, files in os.walk(root):
        for each in files: 
            if len(paths) == Max:
                return paths
            paths.append(os.path.join(previous, each))
    return paths

def combineWithFile(filename, pathList):
    newPaths = []
    for i in pathList:
        newPaths.append(os.path.join(i, filename))
    return newPaths

def savePaths(outfile, pathList):
    with open(outfile, "wa") as file:
        for i in paths:
            file.write(i+"\n")
        file.close()

def parse():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--generate-dirs", default=False, action="store_true" , help="Generate directory paths. If not specified jump to LFI")
    group.add_argument("--generate-files", default=False, action="store_true" , help="Generate file paths. If not specified jump to LFI")
    group.add_argument("--generate-custom", default=False, action="store_true" , help="Generate paths with custom file. If not specified jump to LFI")

    parser.add_argument("-o", "--out-file", default="", type=str, help="Write generated paths to file")
    parser.add_argument("-n", "--number", default=500, type=int, help="Number of maximum paths to be generated")
    parser.add_argument("-s", "--string", default="", type=str, help="Filename to be included in the paths")
    
    args = parser.parse_args()
    return [parser, args]

def Banner():
    banner = """
##############################################################
 
     _     ______ _____      _                  _           
    | |    |  ___|_   _|    | |                | |          
    | |    | |_    | | _ __ | |_ _ __ _   _  __| | ___ _ __ 
    | |    |  _|   | || '_ \| __| '__| | | |/ _` |/ _ \ '__|
    | |____| |    _| || | | | |_| |  | |_| | (_| |  __/ |   
    \_____/\_|    \___/_| |_|\__|_|   \__,_|\__,_|\___|_|  


############################################### By Diego Bernal
                """
    print banner

if __name__ == "__main__":

    parser, args = parse()

    if len(sys.argv) == 1:
        Banner()
        parser.print_usage()
        print
        sys.exit(0)

    # figure out what to do when no option

    if args.__dict__["generate_dirs"] or args.__dict__["generate_files"] or args.__dict__["generate_custom"]:
        
        maxPaths = args.__dict__["number"]
        file_str = args.__dict__["string"]

        if args.__dict__["generate_dirs"]:
            paths = generatePaths(maxPaths)
        elif args.__dict__["generate_files"]:
            paths = generateFiles(maxPaths)
        else:
            if file_str == "":
                print "   --generate_files flag needs a filename to craft the paths. Include it with -s STRING or --string STRING\n"
                parser.print_help()
                sys.exit(1)
            paths = generatePaths(maxPaths)
            paths = combineWithFile(file_str, paths)

    if args.__dict__["out_file"] != "": 
        savePaths(args.__dict__["out_file"], paths)

