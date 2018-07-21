from distutils.dir_util import copy_tree
import os


def ExportGo(Gopath="/Users/username/go/src/"):
    # Get current dir
    fromDirectory = os.getcwd()
    # get current dir name
    foldername = os.path.basename(fromDirectory)

    # copy subdirectory example
    # combine current dir with go-path
    toDirectory = str(Gopath)+foldername

    # Get all subdir abs path
    from glob import glob
    listdir = glob("./*/")
    print(listdir)
    for folder in listdir:
        copy_tree(fromDirectory + folder[1:-1], toDirectory+folder[1:-1])

# d = '.'
# listFolder = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]
# print(listFolder)


def main():
    ExportGo()


if __name__ == '__main__':
    main()
