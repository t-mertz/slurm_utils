#!/usr/bin/env python

from distutils.core import setup
import setuptools
import shutil

"""
try:
    import numpy
except ImportError:
    print("ERROR: `numpy` required! Please install numpy first.")
    sys.exit(1)
"""

NAME = 'ssubmit'
VERSION = '0.2dev1'

setup(
    name=NAME,
    version=VERSION,
    author='Thomas Mertz',
    url='http://www.thomasmertz.eu',
    license='GNU GPL',
    #py_modules=['core', 'parameters', 'ini', 'common', 'util', 
    #        'runscancels', 'runstatus', 'runsubmit', 'scancel'],
    #data_files=[('config', 'config.ini'),]
    packages=setuptools.find_packages(),
    install_requires='numpy',
    package_data={
        'config' : ['config.ini'],
    }
)
import sys, os
import site


# check if installed flag has been set
flag_path = os.path.expanduser(os.path.join('~','._ssubmit_installed'))
installed_flag = os.access(flag_path, os.F_OK)

site_dir = site.getusersitepackages()
if isinstance(site_dir, list):
    site_dir = site_dir[0]

pyver = sys.version[:3]
site_dir = os.path.join(site_dir, NAME + "-" + VERSION + "-py" + pyver + ".egg")


# set shell aliases when install
if sys.argv[1].strip() == "install":
    if not installed_flag:
        print("Registering shell aliases")
        # set shell alias for ssubmit
        submit_comment_str = "# Type `ssubmit` to run the ssubmit SLURM utility.\n"
        submit_alias_str = "alias ssubmit='python {}'\n".format(os.path.join(site_dir, 'core', 'runsubmit.py'))
        
        # set shell alias for sstatus
        status_comment_str = "# Type `sstatus` to run the sstatus SLURM utility.\n"
        status_alias_str = "alias sstatus='python {}'\n".format(os.path.join(site_dir, 'core', 'runstatus.py'))

        # set shell alias for scancels
        cancel_comment_str = "# Type `scancels` to run the scancels SLURM utility.\n"
        cancel_alias_str = "alias scancels='python {}'\n".format(os.path.join(site_dir, 'core', 'runcancels.py'))

        with open(os.path.expanduser(os.path.join('~', '.bashrc')), 'a') as bashrc:
            bashrc.write(submit_comment_str)
            bashrc.write(submit_alias_str)
            print("submit done...")

            bashrc.write(status_comment_str)
            bashrc.write(status_alias_str)
            print("status done...")

            bashrc.write(cancel_comment_str)
            bashrc.write(cancel_alias_str)
            print("cancel done...")
        
        # set installed flag
        flag_file = open(flag_path, 'w')
        flag_file.write('')
        flag_file.close()

        print("Done registering shell aliases")
elif sys.argv[1].strip() == "uninstall":
    if installed_flag:
        print("Removing shell aliases")
        # remove aliases
        
        submit_comment_str = "# Type `ssubmit` to run the ssubmit SLURM utility.\n"
        submit_alias_str = "alias ssubmit='python {}'\n".format(os.path.join(site_dir, 'core', 'runsubmit.py'))
        

        # set shell alias for sstatus
        status_comment_str = "# Type `sstatus` to run the sstatus SLURM utility.\n"
        status_alias_str = "alias sstatus='python {}'\n".format(os.path.join(site_dir, 'core', 'runstatus.py'))

        # set shell alias for scancels
        cancel_comment_str = "# Type `scancels` to run the scancels SLURM utility.\n"
        cancel_alias_str = "alias scancels='python {}'\n".format(os.path.join(site_dir, 'core', 'runcancels.py'))

        rc_strings = [submit_comment_str, submit_alias_str, status_comment_str, status_alias_str, \
                        cancel_comment_str, cancel_alias_str]

        # file paths
        bashrc_path = os.path.expanduser(os.path.join('~', '.bashrc'))
        tmp_path = os.path.expanduser(os.path.join('~', '.bashrc_tmp'))

        # copy only other entries to tmp file
        bashrc_in = open(os.path.expanduser(os.path.join('~', '.bashrc')), 'r')
        bashrc_out = open(os.path.expanduser(os.path.join('~', '.bashrc_tmp')), 'w')

        for line in bashrc_in:
            if line not in rc_strings:
                bashrc_out.write(line)
        
        bashrc_in.close()
        bashrc_out.close()

        # replace old .bashrc by tmp file
        os.rename(bashrc_path, tmp_path)

        # remove flag
        os.unlink(flag_path)
        
        print("Done removing shell aliases")
    
    # remove database folder
    shutil.rmtree(os.path.expanduser(os.path.join("~", ".ssubmit")))
