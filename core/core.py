from __future__ import division, print_function
import subprocess
import numpy as np
import sys, os
import logging
from utils import ini, common, util
#import ini
#import lacommon
#import common
import shutil
import glob
import time
import pickle
#import util

PY_VER = sys.version
if int(PY_VER[0]) < 3:
    import exceptions


VERSION = '0.2'
AUTHOR = "Thomas Mertz"

db_dir = os.path.expanduser(os.path.join('~','.ssubmit'))
util.assert_dir(db_dir)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



# ================================================================================



class ConfigPathError(Exception):
    """
    Raised when invalid config path is detected.
    """
    def __init__(self, value=''):
        self.value = value
    
    def __str__(self):
        return repr(self._value)

class MissingDirectoryError(Exception):
    """
    Raised when directory is not found by StatusChecker.
    """
    def __init__(self, value=''):
        self.value = value
    
    def __str__(self):
        return repr(self._value)

class MissingOutfileError(Exception):
    """
    Raised when no outfile is found by StatusChecker.
    """
    def __init__(self, value=''):
        self.value = value
    
    def __str__(self):
        return repr(self._value)



# ================================================================================



class Jobs(object):
    """
    Handles job success and fail count.
    """
    def __init__(self):
        self._success = 0
        self._skipped = 0
        self._failed = 0
        self._total = 0


    def success(self):
        """
        Register one successful job.
        """
        self._success += 1
        self._total += 1

    def failed(self):
        """
        Register one failed job.
        """
        self._failed += 1
        self._total += 1
    
    def skipped(self):
        """
        Register one skipped job.
        """
        self._skipped += 1
        self._total += 1
    
    def reset(self):
        """
        Reset job counters.
        """
        self._success = 0
        self._failed = 0
        self._total = 0
    
    def set_total(self, total):
        """
        Set total number of jobs.
        """
        self._total = total
    
    def get_success_ratio(self):
        return self._success / self._total
    
    def get_fail_ratio(self):
        return self._failed / self._total

    def get_fail(self):
        return self._failed

    def get_success(self):
        return self._success
    
    def get_skipped(self):
        return self._skipped
    
    def get_total(self):
        return self._total



# ==================================================================================



class JobStatus(Jobs):
    def __init__(self):
        Jobs.__init__(self)
        self._pending = 0
        self._running = 0
        self._cancelled = 0
    
    def pending(self):
        self._pending += 1
        self._total += 1
    
    def running(self):
        self._running += 1
        self._total += 1
    
    def cancelled(self):
        self._cancelled += 1
        self._total += 1

    def get_pending(self):
        return self._pending

    def get_running(self):
        return self._running

    def get_cancelled(self):
        return self._cancelled


# Here the actual program begins

# ================================================================================



class ParameterIterator(object):

    def __init__(self):
        self._supdate = dict()
        self._settings = dict()
        self._params = None
        self._pid_inds = []

        self._dformat_str = ""
        self._pformat_str = ""
        self._pformat_list_all = []

    def fix_settings_format(self):

        if self._params is not None:
            # fix formatting of parameters
            if 'par_in_dirname' in self._settings and \
                len(self._settings['par_in_dirname'].split(',')) > 0:
                self._settings.update([['par_in_dirname', \
                    [v.strip() for v in self._settings['par_in_dirname'].split(',')]]])
            else:
                self._settings.update([['par_in_dirname', self._params.get_names()]])
            
            if not common.list_prod([p in self._params.get_names() for p in self._settings.get('par_in_dirname')]):
                raise RuntimeError("Invalid parameter found in `par_in_dirname` settings.")

    def iterate(self):
        """
        Iterate through parameters and call `execute`.
        The method `execute` is overridden by subclasses.
        """

        for job_idx, cur_p in enumerate(self._params):
            self.execute(job_idx, cur_p)
    
    def finalize(self):
        pass
    
    def execute(self, job_idx, params):
        pass
    
    def setup_default_settings(self):
        """
        Setup the default settings dictionary.
        """

        #raise NotImplementedError("ParameterIterator.setup_default_settings")

        settings = dict()
        settings.update([['script_path', 'slurm.sh']])
        settings.update([['config_path', 'config.ini']])
        settings.update([['submit_as', 'sbatch']])
        settings.update([['overwrite_dir', False]])
        settings.update([['test_mode', True]])
        settings.update([['jobname_prefix', '']])
        settings.update([['logfile_name', 'slurm.log']])
        settings.update([['cmd_arguments', '']])
        settings.update([['write_parameter_info', True]])
        settings.update([['use_index', False]])

        self._settings = settings
    
    def update_ini_settings(self):
        """
        Update default settings with config file.
        """
        #raise NotImplementedError("ParameterIterator.update_ini_settings")

        try:
            params, f_settings = ini.parameters_from_ini(self._settings.get('config_path'))
        except ini.IniFormatError as e:
            sys.stdout.write('Error! Wrong format in config file:\n')
            sys.stdout.write(str(e) + '\n')
            sys.exit(1)
        except IOError:
            sys.stdout.write('Error! Could not read file `{}`.\n'.format(self._settings.get('config_path')))
            sys.exit(1)
        except TypeError:
            sys.stdout.write('Error! Could not read file `{}`.\n'.format(self._settings.get('config_path')))
            sys.exit(1)
        except:
            raise

        # set params and update settings
        self._params = params
        self._settings.update(f_settings)

    def update_cmd_settings(self):
        """
        Update default settings with command line options.
        """
        
        #raise NotImplementedError("ParameterIterator.update_cmd_settings")
        
        self._settings.update(self._supdate)
    
    def create_dformat_str(self):
        """
        Get format string for directory name.
        """
        num_dname_vals = len(self._settings['par_in_dirname'])
        dtypes = [ type(self._params.get_values_ax(name)[0]) for name in self._settings['par_in_dirname']]
        decimals = None
        format_str = util.generate_format_spec(num_dname_vals, "_", dtypes, decimals)

        if self._settings['use_index']:
            format_str = util.generate_named_index_format_spec(self._settings['par_in_dirname'], "_")

        self._dformat_str = format_str

    def create_par_in_dirname_inds(self):
        """
        Create array with indices of parameters in directory names.
        """
        
        pid_inds = []
        for p in self._settings.get('par_in_dirname'):
            pid_inds.append(self._params.get_axis(p))
        
        self._pid_inds = np.asarray(pid_inds)

    def get_dirname(self, plist, job_idx):
        if self._settings['use_index']:
            return self._dformat_str.format(*list(np.asarray(self._params.get_inds_per_ax(job_idx))[self._pid_inds]))
        else:
            return self._dformat_str.format(*list(np.asarray(plist)[self._pid_inds]))


    def create_pformat_str(self, all=False):

        if all:
            pars = self._params.get_names()
            num = self._params.get_dim()
            dtypes = self._params.get_types()
        else:
            pars = self._settings['par_in_dirname']
            num = len(self._settings['par_in_dirname'])
            dtypes = [ type(self._params.get_values_ax(name)[0]) for name in self._settings['par_in_dirname']]
        
        decimals = None
        format_str = util.generate_format_spec(num, "_", dtypes, decimals)
        
        format_ids = format_str.split("_")
        format_strs = ["{name}={id}, ".format(name=name, id=format_ids[i]) for i,name in enumerate(pars)]
        format_str = ""
        for sstr in format_strs:
            format_str += sstr
        if len(format_str) > 0:
            format_str = format_str[:-2]

        if all:
            self._pformat_str_all = format_str
        else:
            self._pformat_str = format_str
    
    def get_pformat_str(self, plist, all=False):

        if all:
            return self._pformat_str_all.format(*plist)
        else:
            return self._pformat_str.format(*plist[self._pid_inds])
    
    def create_pformat_list(self):
        """
        Create list of formatter strings for all parameters.
        """
        num = self._params.get_dim()
        dtypes = self._params.get_types()
        formatter = util.generate_format_spec(num, "_", dtypes, None)
        formatter = formatter.split("_")

        self._pformat_list_all = formatter

    def create_dformatlist_str(self):
        """
        Create formatter string for list of all parameters listed in directory names.
        """
        format_str = util.generate_named_index_format_spec(self._settings['par_in_dirname'], "_", "=")
        formatter_lst = format_str.split("_")
        formatter = ", ".join(formatter_lst)

        self._dformatlist_str = formatter

# ================================================================================



class JobDB(object):
    
    _db_path = os.path.join(db_dir, 'jobs.db')

    def __init__(self):
        
        # initialize as False
        # creating an empty db file updates value to True
        self._isempty = False

        if not self.check_job_db():
            self.create_empty_job_db()
        else:
            pass

    def create_empty_job_db(self):
        """
        Create an empty database file in the `db_path` location.
        """
        #with open('jobs.db', 'wb') as db:
        #    pass
        new_db = []
        db_file = open(self._db_path, 'wb')

        pickle.dump(new_db, db_file, -1)

        db_file.flush()
        db_file.close()

        self._isempty = True
    
    def update_job_db(self, plist, dirname, job_id):
        """
        Update job database with parameter list, directory name, job index and a time stamp.
        """

        submit_time = time.time()
        #with open('jobs.db', 'ab') as db:
        #    db.write(".{},{},{}".format(dirname, job_idx, submit_time))

        # read old data
        db_file = open(self._db_path, 'rb')
        db_data = pickle.load(db_file)
        db_file.close()


        # write new data
        db_data.append([plist, dirname, job_id, submit_time])
        db_file = open(self._db_path, 'wb')
        pickle.dump(db_data, db_file, -1)
        db_file.flush()
        db_file.close()

        # database is no longer empty
        self._isempty = False
    
    def check_job_db(self):
        """
        Check if job database file exists.
        """
        return True if util.fexists(self._db_path) else False
    
    def isempty(self):
        """
        Check if empty flag attribute is set.
        """
        return self._isempty
    
    def read_job_db(self):
        """
        Read the job database file. Returns empty job array if database file 
        does not exist or database is empty.
        """
        
        # check if database file exists and is not empty
        if self.check_job_db() and not self.isempty():
            """
            db_list = []
            with open('jobs.db', 'rb') as db:
                for line in db:
                    db_list += line.split('.')
            
            njobs = len(db_list)
            times = np.zeros(njobs)
            dirnames = np.zeros(njobs)
            job_idx = np.zeros(njobs)

            for i,itm in enumerate(db_list):
                data = itm.split(',')
                dirnames[i] = data[0]
                job_idx[i] = data[1]
                times[i] = data[2]
            
            self.job_db = np.vstack([dirnames, job_idx, times])
            """
            db_file = open(self._db_path, 'rb')
            #for line in db_file:
            #    print(line)
            #db_data = [[]]
            db_data = pickle.load(db_file)
            db_file.close()
            return np.vstack(db_data)
        else:
            # database is empty, return empty job array
            return np.vstack([[]])

    def find_in_job_db(self, plist, ret='all'):
        job_db = self.read_job_db()

        db_entry = job_db[np.where(job_db[:, 0] == plist)[0]]

        if ret == 'id':
            return db_entry[2]
        elif ret == 'dirname':
            return db_entry[1]
        elif ret == 'all':
            return db_entry



# ===============================================================================



class Submitter(ParameterIterator, JobDB):
    """
    Handles the submission of SLURM jobs. A job database is created for each job 
    and can be used to check the status of each particular job.
    """

    _logfile_name = "ssubmit.log"

    def __init__(self, argv):

        # call base class constructors
        JobDB.__init__(self)
        ParameterIterator.__init__(self)

        # determine the execution mode and supdate settings
        self.process_input(argv)
        #print(self._mode, self._supdate.get('ini_dst'))

        if self._mode == 'print_ini':
            # copy the default ini file to the destination
            copy_default_ini(self._supdate.get('ini_dst'))
        elif self._mode == 'run':
            
            # load the job database
            self._job_db = self.read_job_db()

            # setup the correct settings.
            # this is done in order: default > ini > commandline
            # later settings override earlier settings.

            self.setup_default_settings()
            print(self._settings.get('test_mode'))
            self.update_ini_settings()
            print(self._settings.get('test_mode'))
            self.update_cmd_settings()
            print(self._settings.get('test_mode'))
            self.fix_settings_format()
            print(self._settings.get('test_mode'))

            self._job_count = Jobs()

            # create array with indices of parameters in directory names
            self.create_par_in_dirname_inds()

            # setup format strings for directory names and parameter lists
            self.create_dformat_str()
            self.create_dformatlist_str()
            self.create_pformat_str()
            self.create_pformat_str(all=True)
            self.create_pformat_list()

    def get_mode(self):
        """
        Getter method for execution mode. 
        Possible values are:

        * 'help'        : displays help
        * 'print_ini'   : copies default ini file to directory
        * 'run'         : runs program
        """
        return self._mode
    
    def process_input(self, argv):
        """
        Determine if the program is supposed to run or print help.
        If the mode is `run`, also determine the settings from `argv`.
        """
        argc = len(argv[1:])
        if argc < 1:
            self._mode = 'help'
        else:
            self._mode = 'run'
        
        if self._mode == 'run':
            supdate = dict()

            num_set = [] # list of numbers set

            #print(argc, argv)

            i = 1
            while (i <= argc):
                
                if argv[i].strip() == "-f":
                    if argc >= i+1:
                        try:
                            supdate.update([['config_path', argv[i+1]]])
                        except:
                            raise ConfigPathError("Invalid config path: " + str(argv[i+1]))
                    else:
                        supdate.update([['config_path', '.']])
                        
                    i += 2
                elif argv[i].strip() == '-F':
                    self._mode = 'print_ini'

                    #print(i)

                    if argc >= i+1:
                        dst = argv[i+1]
                    else:
                        dst = '.'
                    supdate.update([['ini_dst', dst]])
                    break
                else:
                    try:
                        num = int(argv[i])
                    except:
                        raise
                    num_set.append(num)
                i += 1
            
            if len(num_set) == 1:
                supdate.update([['start_index', 1]])
                supdate.update([['num_submits', num_set[0]]])
            elif len(num_set) > 1:
                supdate.update([['start_index', num_set[0]]])
                supdate.update([['num_submits', num_set[1]]])

            self._supdate = supdate


    def display_help(self):
        """
        Display welcome screen and help message in the console.
        """
        
        sep = "-"*80 + "\n"
        vert = "|"
        help_msg = "\n"
        help_msg += sep
        help_msg += vert + " "*21 + "You are running ssubmit version {}".format(VERSION) + " "*22 + vert + "\n"
        help_msg += "|" + " "*78 + "|\n"
        help_msg += "|" + " "*23 + "Copyright (c) 2016 {}".format(AUTHOR)  + " "*24 + vert + "\n"
        help_msg += sep
        help_msg += "\nHelp mode is active\n\n"
        help_msg += sep
        help_msg += "\nCommand list:\n"
        help_msg += get_underline("Command list:")
        help_msg += ">> ssubmit <n>\nSubmit the jobs with indices 1...n\n"
        help_msg += "<n> = number of submits\n"
        help_msg += "\n>> ssubmit <s> <n>\nSubmit the jobs with indices s...s+n-1\n"
        help_msg += "<s> = start index\n"
        help_msg += "<n> = number of submits\n"
        help_msg += "\n-f <path>   (default <path>=./config.ini)\n" + " "*12 + "Path to the .ini configuration file.\n"
        help_msg += "\n-F <path>   (default <path>=.)\n" + " "*12 + "Save default config.ini file to the path.\n"
        
        
        sys.stdout.write(help_msg)
    

    def iterate(self):
        """
        Iterate through parameters and call `execute`.
        This overrides the base class method and implements iteration only over select 
        parameters.
        """

        # get first and last index from settings
        first = self._settings.get('start_index')
        last = first + self._settings.get('num_submits') - 1

        # check if number of submits from input is reasonable
        changed_num, num = self.get_num_jobs(first, self._settings.get('num_submits'))
        if changed_num:
            last = first + num - 1
            self.log("INFO: Number of jobs specified ({}) larger than total number of jobs ({}). Overriding.\n".format(self._settings.get('num_submits'), self._params.get_maxnum() + 1))
            self._settings.update([['num_submits', num]])
        
        # log number of jobs to submit 
        self.log("Submitting jobs {first} to {last} of {total}:\n".format(first=first, last=last, total=self._params.get_maxnum()), new=True)

        # do the iteration, call execute for every job
        for job_idx, cur_p in enumerate(self._params[first-1:last]):
            self.log("{}. Submitting job for ".format(first+job_idx) + self._pformat_str.format(*cur_p) + " | indices: " + self._dformatlist_str.format(*self._params.get_inds_per_ax(job_idx)))
            self.execute(first-1+job_idx, cur_p)

    def get_num_jobs(self, start, num):
        """
        Get number of jobs to submit. Takes into account the maximal number of
        jobs available.

        Returns:
        bool num changed?
        int num
        """
        total = self._params.get_maxnum() + 1
        if start + num > total:
            return True, total - start
        else:
            return False, num

    def finalize(self):
        """
        Print final information about success to logfile.
        """

        # get first and last index from settings
        first = self._settings.get('start_index')
        last = first + self._settings.get('num_submits') - 1

        # get number of submits from settings
        num_submits = self._settings.get('num_submits')

        # determine if there has been an error, set the summary string accordingly
        if self._job_count.get_total() == num_submits and \
            self._job_count.get_success() == self._job_count.get_total():
            err_str = "without"
        else:
            err_str = "with"

        # get the grammar right
        if num_submits > 1:
            job_str = "jobs"
        else:
            job_str = "job"
        
        # compose and log the summary string
        self.log("\nSummary:")
        self.log(get_underline("Summary:"))
        self.log("Submission of {} {} completed {} errors.".format(num_submits, job_str, err_str))
        self.log("\n{:8s}: {:3d}".format("Success", self._job_count.get_success()))
        self.log("{:8s}: {:3d}".format("Skipped", self._job_count.get_skipped()))
        self.log("{:8s}: {:3d}\n".format("Failed", self._job_count.get_fail()))

        # log the next job index
        if last >= self._params.get_maxnum():
            self.log("All {} jobs submitted.".format(self._params.get_maxnum()))
        else:
            self.log("Next job: {}".format(last+1))

    def execute(self, job_idx, cur_p):
        
        # get directory name
        dirname = self.get_dirname(cur_p, job_idx)

        # create directory if it doesn't exist
        retval = util.assert_dir(dirname)

        # else if settings.get('overwrite')
        if not retval or self._settings.get('overwrite'):

            # if settings.get('submit_as') is 'sbatch'
            if self._settings.get('submit_as') == 'sbatch':
                retval, message = self.submit_sbatch(dirname, cur_p)
            
            if retval:
                self._job_count.success()

                # add job to job database
                job_id = message.strip().split()[-1]
                self.update_job_db(cur_p, os.path.realpath(dirname), job_id)

                self.log("> Submission succeeded. ({})\n".format(message))
            else:
                self._job_count.failed()
            
                self.log("> Submission failed. ({})\n".format(message))
        else:
            self.log("> Directory existed and overwrite is disabled. Skipping this value.\n")
            self._job_count.skipped()

    def submit_sbatch(self, dirname, plist):
        
        # create wildcard list
        wildcard_list = get_wildcard_list(self._params)

        # name and path of the script file
        filename = os.path.basename(self._settings.get('script_path'))
        filepath = os.path.join(dirname, filename)

        # create jobname
        jobname = self._settings.get('jobname_prefix') + dirname

        # copy-replace script file
        #print(self._pformat_list_all)
        #print(plist)
        #replace_items = [fstr.format(p) for fstr, p in zip(self._pformat_list_all, plist)] #.append(jobname)
        replace_items = [str(p) for p in plist]
        replace_items.append(jobname)
        #print(replace_items)
        util.copy_replace(self._settings.get('script_path'), filepath, wildcard_list, replace_items)

        # copy also other files and replace occurrences of parameters
        if 'other_files' in self._settings:
            for filename in self._settings.get('other_files'):
                tmp_filename = os.path.basename(filename)
                tmp_filepath = os.path.join(dirname, tmp_filename)
                util.copy_replace(filename, tmp_filepath, wildcard_list, replace_items)

        print(self._settings.get('test_mode'))
        if not self._settings.get('test_mode'):
            # submit script file
            print("hello")
            p = subprocess.Popen(["sbatch", self._settings.get('cmd_arguments'), '-D', dirname, filepath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out_str, err_str = p.communicate()
        else:
            # pretend submission was successful
            self.log("> Test mode active, not submitting.")
            out_str = "JOB 1 SUBMITTED"
        
        message = out_str

        # determine if submission was successful
        if "FAILED" in message.upper():
            retval = False
        elif "SUBMITTED" in message.upper():
            retval = True
        else:
            retval = False

        # return message
        return retval, message
    
    def submit_srun(self, dirname, plist):
        
        raise NotImplementedError("Submitter.submit_srun")
    
    def log(self, logstring, to_screen=True, new=False):
        
        log_exists = util.fexists(self._logfile_name)
        with open(self._logfile_name, 'a') as logfile:
            if new and log_exists:
                logfile.write("\n" + "-"*80 + "\n\n")
            logfile.write(logstring + "\n")
        
        if to_screen:
            sys.stdout.write(logstring + "\n")



# ====================================================================================



class StatusChecker(ParameterIterator, JobDB):
    """
    Handles status of jobs from job database or output files.
    """

    def __init__(self, argv):
        
        # source of job information
        # a : job database (all)
        # d : directories
        # f : configuration file
        self._src_mode = 'all'

        # jobs to include
        # A : all
        # R : running
        # C : cancelled
        # F : failed
        # P : pending
        self._include = 'A'
        self.process_input(argv)

        if self._mode == 'run':
            ParameterIterator.__init__(self)
            JobDB.__init__(self)
            self._job_db = self.read_job_db()

    def get_mode(self):
        return self._mode


    def process_input(self, argv):
        """
        Process command line arguments.
        """
        
        argc = len(sys.argv[1:])
        if argc < 1:
            self._mode = 'help'
        else:
            self._mode = 'run'
        
        i = 1
        include = ''
        while (i <= argc):
            cur_arg = argv[i].strip()
            if cur_arg[0] == '-' and len(cur_arg) > 1:
                if 'a' in cur_arg:
                    # use job database
                    self._src_mode = 'all'
                if 'd' in cur_arg:
                    # use created directories
                    self._src_mode = 'dir'
                if 'f' in cur_arg:
                    # use config file
                    self._src_mode = 'file'
                if 'A' in cur_arg:
                    # all
                    include += 'A'
                    self._include = include
                if 'R' in cur_arg:
                    # running
                    include += 'R'
                    self._include = include
                if 'C' in cur_arg:
                    # cancelled
                    include += 'C'
                    self._include = include
                if 'F' in cur_arg:
                    # failed
                    include += 'F'
                    self._include = include
                if 'P' in cur_arg:
                    # pending
                    include += 'P'
                    self._include = include
                if cur_arg == '-c':
                    # clear database
                    try:
                        confirm = raw_input("Confirm deletion of job database (y/n): ")
                    except NameError:
                        # use in Python 3.x
                        confirm = input("Confirm deletion of job database (y/n): ")
                        
                    if confirm.lower() in ['y', 'yes']:
                        raise NotImplementedError("clear database option")
                    else:
                        print("Clear database cancelled.")
                        sys.exit(0)
            else:
                raise RuntimeError("Unrecognized commandline option {}".format(argv[i]))
            i += 1


    def display_help(self):
        """
        Display welcome screen and help message in the console.
        """
        
        sep = "-"*80 + "\n"
        vert = "|"
        help_msg = "\n"
        help_msg += sep
        help_msg += vert + " "*21 + "You are running sstatus version {}".format(VERSION) + " "*22 + vert + "\n"
        help_msg += "|" + " "*78 + "|\n"
        help_msg += "|" + " "*23 + "Copyright (c) 2016 {}".format(AUTHOR)  + " "*24 + vert + "\n"
        help_msg += sep
        help_msg += "\nHelp mode is active\n\n"
        help_msg += sep
        help_msg += "\nCommand list:\n"
        help_msg += get_underline("Command list:")
        help_msg += ">> sstatus \nCheck status of the jobs specified by current `config.ini` file\n"

        help_msg += "\n-a" + " "*10 + "Check status of all jobs in the job database.\n"
        help_msg += "\n-d" + " "*10 + "Check status of all jobs running in subdirectories of the current working directory.\n"
        help_msg += "\n-f" + " "*10 + "Check status of all jobs specified in the configuration file in the current working directory.\n"
        
        help_msg += "\nFilters:\n"
        help_msg += "-A" + " "*10 + "Show all jobs.\n"
        help_msg += "-R" + " "*10 + "Show running jobs.\n"
        help_msg += "-C" + " "*10 + "Show cancelled jobs.\n"
        help_msg += "-F" + " "*10 + "Show failed jobs.\n"
        help_msg += "-P" + " "*10 + "Show pending jobs.\n"

        help_msg += "\n-c" + " "*10 + "Clear job database.\n"

        
        
        
        sys.stdout.write(help_msg)
    
    def find_last_job(self, dirname):
        """
        Return the highest job index from outfiles in the directory `dirname`.
        """
        filelist = glob.glob(os.path.join(dirname, "*.out"))
        job_id_list = [int(name.split('.')[0].split('-')[1]) for name in filelist]

        return max(job_id_list) if len(job_id_list) > 0 else None
    
    def check_accounting(self, job_id):
        
        raise NotImplementedError("StatusChecker.check_accounting")

        p = subprocess.Popen(['sacct', '-j', str(job_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        try:
            sacct_outstr = p.communicate()[0].split('\n')[2]
            #print sacct_outstr

            job_no = sacct_outstr.split()[0]
            slurm_status = sacct_outstr.split()[5]

            if slurm_status.lower() == 'cancelled':
                self._job_count.cancelled()
            elif slurm_status.lower() == 'failed':
                self._job_count.fail()
            elif slurm_status.lower() == 'running':
                self._job_count.running()
            elif slurm_status.lower() == 'pending':
                self._job_count.pending()

            #print sacct_outstr

        except:
            slurm_status = "job ID not found"
        
        #self._pformat_str.format(*cur_p)

        #self.log(std_string + "job {0} {1}".format(job_id, slurm_status))

        return slurm_status

    def check_squeue(self, job_id):
        
        raise NotImplementedError("StatusChecker.check_squeue")
    
    def check_outfile(self, job_id):
        raise NotImplementedError("StatusChecker.check_outfile")
    
    def find_in_dir(self, plist, job_idx):
        """
        Find job ID from out files in subdirectory corresponding to `plist`.
        """
        dirname = self.get_dirname(plist, job_idx)
        outfiles = glob.glob(os.path.join(dirname, "*.out"))

        job_id = int(outfiles.sort()[-1].split(".")[0].split('-')[1])

        return job_id

    def iterate(self):
        """
        Iterate over the parameters and call the `execute` method.

        This overloads the base class method to implement different modes.
        The `file` mode simply executes the base class method.
        """
        
        if self._src_mode == "all":
            raise NotImplementedError("option -a")

        elif self._src_mode == "dir":

            #raise NotImplementedError("option -d")

            # get list of subdirectories
            dirlist = util.list_dir().sort()

            # iterate over list
            for idx, dir in enumerate(dirlist):
                # find parameters from dirname
                plist = get_plist(dir)
                linear_idx = self._params.get_number(plist) # linear index of the parameters
                self.execute(linear_idx, plist)
            
        elif self._src_mode == "file":
            #raise NotImplementedError("option -f")

            # use base class method
            ParameterIterator.iterate(self)

    def execute(self, job_idx, plist):
        """
        Call the status checks and print outputs to screen.
        """

        dirname = self.get_dirname(plist, job_idx)

        status = None

        # find job in job_db
        try:
            #idx = np.where(self._job_db[0] == os.path.realpath(dirname))[0]
            #job_id = self._job_db[1, idx]
            job_id = self.find_in_job_db(plist, 'id')
        except:
            try:
                job_id = self.find_in_dir(plist, job_idx)
            except MissingDirectoryError:
                status = "Job and directory not found"
            except MissingOutfileError:
                status = "No output file found"

        # if job ID could be retrieved
        if status is None:
            status = self.check_squeue(job_id)
            if status == "job ID not found":
                status = self.check_accounting(job_id)
            
            if status == "job ID not found":
                status = self.check_outfile(job_id)

        sep = " "*4
        self.log("{job_id}{sep}{parameters}{sep}{dirname}{sep}{status}".format(job_id=job_id, sep=sep, parameters=plist, dirname=dirname,status=status))

    def log(self, logstring):

        sys.stdout.write(logstring + "\n")

class DataProcessor(ParameterIterator):
    """
    Defines an instance that allows easy iteration through data folders for 
    data processing purposes.
    In each folder the method `process` is executed.
    """

    def process(self):
        """
        Overload this function to do some processing.
        """
        pass

# ==================================================================================
# ==================================================================================

# global static methods

def get_dist_path():
    return os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]

def copy_default_ini(dst):

    path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
    
    #print(path, dst)

    shutil.copy(os.path.join(path, 'config', 'config.ini'), dst)


def get_underline(string):
    """
    Return an underline string of the same length as `str`.
    """
    return "="*len(string) + "\n"

def get_wildcard(name):
    """
    Create a wildcard of the form `<NAME>_VAL` from name.
    This is supposed to ensure that when replacing the wildcard in the bash script,
    no accidental mismatch occurs.
    """
    return name.upper() + "_VAL"

def get_wildcard_list(params):
    """
    Return a list of wildcard strings of the form `<PARNAME>_VAL`, where <PARNAME> are 
    the (uppercase) names of the parameters in params. The additional wildcard `JOBNAME` is included.
    """
    wildcard_list = []

    for name in params.get_names():
        wildcard_list.append(get_wildcard(name))
    
    # include jobname
    wildcard_list.append("JOBNAME")

    return wildcard_list

def main(mode, *argv):
    try:
        if mode is 'submit':
            ssub_iter = Submitter(argv)
        elif mode is 'status':
            ssub_iter = StatusChecker(argv)
        else:
            sys.exit()
        
        if ssub_iter.get_mode() == 'help':
            ssub_iter.display_help()
        elif ssub_iter.get_mode() == 'run':
            ssub_iter.iterate()
            ssub_iter.finalize()
    except NotImplementedError as e:
        print("ERROR: Method {} not implemented.".format(str(e)))
