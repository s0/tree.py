tree.py
=======

**tree.py** is a small utility that displays input from stdin in a tree-like structure. It takes a large amount of inspiration from Steve Baker's original and widely deployed tree utility: http://mama.indstate.edu/users/ice/tree/

**tree.py** operates in a very different way to the traditional **tree** command, it instead takes input from stdin (so you can pipe it data) and will try and parse it and present it in an intuitive tree-like format.


* [Usage](#usage)
  * [Basic Usage](#basic-usage)
  * [Usage with **find**](#usage-with-find-or-another-tool-with-similar-output)
  * [Usage with **grep**](#usage-with-grep)
* [Future Plans](#future-plans)
* [Advanced Usage](#advanced-usage)
  * [Notes](#notes)
* [Copyright](#copyright)


## Usage

### Setup

You can put the file tree.py wherever you like, and set an alias in your `.bashrc` file if you use **bash**, or you can just copy it to your `/usr/bin/` directory: ***Note: this script is written in python3 not python2, so make sure it's being run by the correct executable! (check the shebang)***

    > sudo cp tree.py /usr/bin/

### Basic Usage

The traditional way to use tree.py *will be* with no commands (or with a path passed in) to display the whole directory tree of a target. ***Note: this feature is actually not implemented yet, use `find <path> | tree -i` for the moment.***

    > tree [path]

For Example:

    > tree ~/foo/bar
    
### Usage with find *(or another tool with similar output)*

When you want to pipe data from another process into tree.py, you need to use the `--input-mode` or `-i` command-line flag.

    > find . | tree -i
    
Example Output:

    .
    ├── .git
    │   └── ...
    ├── COPYING
    ├── DISCLAIMER
    ├── README.md
    └── tree.py
    
    23 directories, 34 files

You can start to build up powerful commands that display in a nice tree-like way, for example, if you were to filter the above file names like so:

    > find . | grep head
    
You would get this result:

    ./.git/logs/refs/heads
    ./.git/logs/refs/heads/master
    ./.git/refs/heads
    ./.git/refs/heads/master

And piped into tree.py, it display like so:

    .
    └── .git
        ├── logs
        │   └── refs
        │       └── heads
        │           └── master
        └── refs
            └── heads
                └── master
                
    7 directories, 2 files

### Usage with grep

If you are using grep to search for text within multiple files, tree.py can also accept this input, and display a line-match count for each file. For this, as it is not *normal* input, you need to pass in `-i grep` or just `-i g`.

    > grep as ./COPYING ./DISCLAIMER | tree -i g
    
Resulting In:

    .
    ├── [2] COPYING
    └── [1] DISCLAIMER
    
    1 directory, 2 files
    
And here's a nice example with xargs and find too:

    > find . -type f | xargs grep 'as' | tree -i g
    
Resulting In:

    .
    ├── .git
    │   ├── [2] COMMIT_EDITMSG
    │   ├── [1] HEAD
    │   ├── [2] config
    │   ├── hooks
    │   │   ├── [1] commit-msg.sample
    │   │   ├── [6] pre-commit.sample
    │   │   ├── [2] pre-push.sample
    │   │   ├── [42] pre-rebase.sample
    │   │   ├── [3] prepare-commit-msg.sample
    │   │   └── [3] update.sample
    │   ├── [1] packed-refs
    │   └── refs
    │       └── remotes
    │           └── origin
    │               └── [1] HEAD
    ├── [2] COPYING
    ├── [1] DISCLAIMER
    └── [18] tree.py

    6 directories, 14 files


## Future Plans


* Implement tree for non-stdin usage (i.e. without needing `-i`)
* More input file formats
* Ability to display information on files such as file permissions, size, user, group, timestamps etc...


## Advanced Usage

    > tree.py [-h] [-i [none|normal|grep|g|n] ] [-c none|always]
          
    -h, --help                 show the help message
    
    -i, --mode, --input-mode   The input type. If ommitted, the default type is
                               "none", and the directory tree is walked, if -i is
                               given with no argument, then "normal" is used
                               
                               Values:
                                - none:           (default when -i is not included in the command)
                                
                                - normal (or n):  (default when -i is included, but no value given)
                                                  Accept input which is one filename per line
                                                  
                                - grep (or g):    Accept input that is like grep multi-file output
                                                  (i.e. file: match for each line, with single files
                                                  possibly appearing multiple times)
                        
    -c, --color, --colour      Use color in the tree.
    
                               Values:
                                - none:           don't
                                - always:         do
                                
### Notes

**tree.py** *loosely* uses the environment variables `LS_COLORS` and `TREE_COLORS` to decide how to color the output. `TREE_COLORS` is given a higher priority, overriding each individual 'match' in LS_COLORS. You can also define `count` and `bin` to set colours for when you pipe grep input into tree to colour the matches.


## Copyright

Copyright © 2013 Sam Lanning <sam@samlanning.com>
This work is free. You can redistribute it and/or modify it under the terms of the Do What The Fuck You Want To Public License, Version 2, as published by Sam Hocevar. See the COPYING file for more details.

