# cython-npm
Cython project management like npm in nodejs. This project is inspired by npm in nodejs.
### Installation
You can easily install by:
```
pip install cython-npm
```

### Quickstart
When using cython, we face the problem of compile cython file. We can do it easily by:
```
import pyximport; pyximport.install()
```
But that it is not recommended to let **pyximport** build code on end user side as it *hooks into their import system*. The best way to cater for end users is to provide pre-built binary packages.
So i wrote a package providing pre-built binary packages easily.
#### Basic use to Complie file or folder:
``` 
from cython_npm.cythoncompile import export
export('examplefile.pyx')
export('./examplefolder')
```
You should do this code once time only.
### Create install file like package.json
You can also compile many files or folders at once time. Create a file name `install.py` in the root of your project/package and write the code below:
```
from cython_npm.cythoncompile import install
Manymodules = [
    # put your modules list here
    examplefile.pyx,
    ./examplefolder
]
install(Manymodules)
```
Run the file before start your project
```
python install.py
```

### Using require('path') as nodejs
You can also relative import in python by `require` function. For example:
```
from cython_npm.cythoncompile import require

# import .pyx file. Will cause error if not compile yet
examplefile = require('../parentpackage') # import cython package from parent folder
examplefile.somefunction()

# it also support relative import .py file
examplefile = require('../parentpackage', recompile=True) 
examplefile.somefunction()

```