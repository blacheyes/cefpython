# Copyright (c) 2012-2014 The CEF Python authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

# Create a setup package.

import sys
import os
import platform
import argparse
import re
import platform
import shutil
import glob
import shutil
import sysconfig

BITS = platform.architecture()[0]
assert (BITS == "32bit" or BITS == "64bit")

PACKAGE_NAME = "cefpython3"

README_FILE = os.getcwd()+r"/README.txt"
INIT_TEMPLATE = os.getcwd()+r"/__init__.py.template"
SETUP_TEMPLATE = os.getcwd()+r"/setup.py.template"
SETUP_CFG_TEMPLATE = os.getcwd()+r"/setup.cfg.template"

def glob_remove(pathname):
    filelist = glob.glob(pathname)
    for f in filelist:
        os.remove(f)

def glob_copy(src_glob, dst_folder):
    for fname in glob.iglob(src_glob):
        print("Copying %s to %s" % (fname, dst_folder))
        if os.path.isdir(fname):
            shutil.copytree(fname,
                    os.path.join(dst_folder, os.path.basename(fname)))
        else:
            shutil.copy(fname,
                    os.path.join(dst_folder, os.path.basename(fname)))

def glob_move(src_glob, dst_folder):
    if not os.path.exists(dst_folder):
        os.mkdir(dst_folder)
    for fname in glob.iglob(src_glob):
        shutil.move(fname,
                os.path.join(dst_folder, os.path.basename(fname)))

def str_format(string, dictionary):
    orig_string = string
    for key, value in dictionary.iteritems():
        string = string.replace("%("+key+")s", value)
    if string == orig_string:
        raise Exception("Nothing to format")
    if re.search(r"%\([a-zA-Z0-9_]+\)s", string):
        raise Exception("Not all strings formatted")
    return string

def main():
    parser = argparse.ArgumentParser(usage="%(prog)s [options]")
    parser.add_argument("-v", "--version", help="cefpython version",
            required=True)
    args = parser.parse_args()
    assert re.search(r"^\d+\.\d+$", args.version), (
            "Invalid version string")

    vars = {}
    vars["APP_VERSION"] = args.version
    vars["PLATFORM"] = sysconfig.get_platform()
    vars["PY_VERSION_DIGITS_ONLY"] = (str(sys.version_info.major) + ""
            + str(sys.version_info.minor)) # "27" or "34"

    print("Reading template: %s" % README_FILE)
    f = open(README_FILE)
    README_CONTENT = f.read()
    f.close()

    print("Reading template: %s" % INIT_TEMPLATE)
    f = open(INIT_TEMPLATE)
    INIT_CONTENT = str_format(f.read(), vars)
    f.close()

    print("Reading template: %s" % SETUP_TEMPLATE)
    f = open(SETUP_TEMPLATE)
    SETUP_CONTENT = str_format(f.read(), vars)
    f.close()

    print("Reading template: %s" % SETUP_CFG_TEMPLATE)
    f = open(SETUP_CFG_TEMPLATE)
    SETUP_CFG_CONTENT = str_format(f.read(), vars)
    f.close()

    installer_dir = os.path.dirname(os.path.abspath(__file__))

    pyVersion = str(sys.version_info.major) +"."+ str(sys.version_info.minor)
    setup_dir = installer_dir+"/"+PACKAGE_NAME+"-"+vars["APP_VERSION"]\
            +"."+BITS+"-py"+pyVersion+"-setup"
    print("Creating setup dir: "+setup_dir)
    os.mkdir(setup_dir)

    package_dir = setup_dir+"/"+PACKAGE_NAME
    #print("Creating package dir")
    #os.mkdir(package_dir)

    print("Creating README.txt from template")
    with open(setup_dir+"/README.txt", "w") as f:
        f.write(README_CONTENT)

    print("Creating setup.py from template")
    with open(setup_dir+"/setup.py", "w") as f:
        f.write(SETUP_CONTENT)

    print("Creating setup.cfg from template")
    with open(setup_dir+"/setup.cfg", "w") as f:
        f.write(SETUP_CFG_CONTENT)

    binaries_dir = os.path.abspath(installer_dir+"/../binaries_"+BITS+"/")
    print("Copying binaries to package dir")
    shutil.copytree(binaries_dir, package_dir)

    os.chdir(package_dir)
    print("Removing .log .pyc .pdb files from the package dir")
    glob_remove("*.log")
    glob_remove("*.pyc")
    glob_remove("*.pdb")

    os.chdir(installer_dir)

    print("Creating __init__.py from template")
    with open(package_dir+"/__init__.py", "w") as f:
        f.write(INIT_CONTENT)

    print("Creating examples dir in package dir")
    os.mkdir(package_dir+"/examples/")

    print("Creating wx dir in package dir")
    os.mkdir(package_dir+"/wx/")

    print("Moving example scripts from package dir to examples dir")
    examples = glob.glob(package_dir+"/*.py")
    for example in examples:
        # Ignore: cefpython_py27.py - dummy API script
        if os.path.basename(example).startswith("cefpython_"):
            continue
        # Ignore: __init__.py
        if os.path.basename(example).startswith("__"):
            continue
        os.rename(example, package_dir+"/examples/"+os.path.basename(example))
    glob_move(package_dir+"/*.html", package_dir+"/examples/")
    glob_move(package_dir+"/*.css", package_dir+"/examples/")
    glob_move(package_dir+"/*.js", package_dir+"/examples/")

    print("Copying wx/ to package dir")
    wx_subpackage_dir = os.path.abspath(installer_dir+"/../../wx/")
    glob_copy(wx_subpackage_dir+"/*", package_dir+"/wx/")

    print("Moving wx examples from wx/examples to examples/wx")
    glob_move(package_dir+"/wx/examples/*", package_dir+"/examples/wx/")
    os.rmdir(package_dir+"/wx/examples/")

    print("Copying package dir examples to setup dir")
    glob_copy(package_dir+"/examples/", setup_dir+"/examples/")

    # Create empty debug.log files so that package uninstalls cleanly
    # in case examples were launched. Issue 149.
    debug_log_dirs = [package_dir,
                      package_dir+"/examples/",
                      package_dir+"/examples/wx/"]
    for dir in debug_log_dirs:
        print("Creating empty debug.log in %s" % dir)
        with open(dir+"/debug.log", "w") as f:
            f.write("")

    print("Setup Package created successfully.")

if __name__ == "__main__":
    main()
