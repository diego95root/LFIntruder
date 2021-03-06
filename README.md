<h1 align="center">
  <br>
  <img src="https://github.com/diego95root/LFIntruder/blob/master/images/Logo.png" alt="Logo" width="30%">
  <br>
  LFIntruder
  <br>
</h1>

<h4 align="center">
  <br>
  Tool to automate the exploitation of potential LFI vulnerabilities
  <br>
  Includes file paths generation
  <br>
  <br>
  <img src="https://img.shields.io/github/license/diego95root/LFIntruder.svg"/>
  <img src="https://img.shields.io/badge/Python-2.7-yellow.svg"/>
  <img src="https://img.shields.io/github/tag/diego95root/LFIntruder.svg">
  <br>
  <br>
  <img src="https://github.com/diego95root/LFIntruder/blob/master/images/initial.png" alt="Logo" width="70%">
  <br>
</h1>

### Features

- Autogeneration of filepaths but custom generation also possible
- GET exploitation
- POST exploitation (where payload is still in URL)
- Incredibly fast
- Multiple levels of depth scanning
- Useful to generate wordlists of filepaths and directories

### Usage

#### Generation of paths

Generate a list of 500 directories in the system and save them to a file:

```terminal
python main.py --generate-dirs -n 500 -o paths.txt
```

Generate a list of 500 file paths in the system and save them to a file:

```terminal
python main.py --generate-files -n 500 -o paths.txt
```

Create a custom list of file paths by supplying a file path and appending it to directories:

```terminal
python main.py --generate-custom -s Dir/test.txt -n 500 -o paths.txt
```

#### LFI detection

Test page with a parameter called ``file`` and 500 paths of files in the system:

```terminal
python main.py -u "http://localhost:80/LFI.php?file=aaa" -n 500 -p file
```

Test page with a file containing file paths:

```terminal
python main.py -u "http://localhost:80/LFI.php?file=aaa" -n 500 -p file -w paths.txt
```

Test page with autogenerated file paths and 4 levels of depth (``../../../``):

```terminal
python main.py -u "http://localhost:80/LFI.php?file=aaa" -n 100 -p file -l 4
```

### TODO

- Implement multithreading
- Improve way of checking for false positives, longer paths are dangerous
