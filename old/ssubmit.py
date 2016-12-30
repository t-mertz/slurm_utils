from __future__ import division, print_function
import subprocess
import numpy as np
import sys, os
import logging
#sys.path.append(os.path.expanduser("~/OneDrive/MSc_Thomas_Mertz/codes/pycommon"))
import ini
import lacommon
import common
import shutil
import glob
import time

PY_VER = sys.version
if int(PY_VER[0]) < 3:
    import exceptions


#TEST_MODE = False

VERSION = '0.1'
AUTHOR = "Thomas Mertz"

db_dir = os.path.expanduser('~/.ssubmit')

class ConfigPathError(Exception):
    """
    Raised when invalid config path is detected.
    """
    def __init__(self, value=''):
        self.value = value
    
    def __str__(self):
        return repr(self._value)

class Jobs(object):
    """
    Handles job success and fail count.
    """
    def __init__(self):
        self._success = 0
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
    
    def get_total(self):
        return self._total

class JobStatus(Jobs):
    def __init__(self):
        Jobs.__init__(self)
        self._pending = 0
    
    def pending(self):
        self._pending += 1
        self._total += 1
    
    def get_pending(self):
        return self._pending

def get_num_jobs(params, start, num):
    """
    Get number of jobs to submit. Takes into account the maximal number of
    jobs available.

    Returns:
    bool num changed?
    int num
    """
    total = params.get_maxnum()
    if start + num > total:
        return True, total - start
    else:
        return False, num

class ParameterIterator(object):

    def iterate(self):
        for job_idx, pj in enumerate(params):
            self.execute(job_idx, pj)
    
    def execute(self, job_idx, params):
        pass

class Submitter(ParameterIterator):
    pass

    def create_empty_job_db(self):
        with open('jobs.db', 'wb') as db:
            pass
    
    def update_job_db(self, dirname, job_idx):
        submit_time = time.time()
        with open('jobs.db', 'ab') as db:
            db.write(".{},{},{}".format(dirname, job_idx, submit_time))

class StatusChecker(ParameterIterator):

    def __init__(self):
        self.db = self.read_job_db()

    def get_mode(self, argv):
        
        argc = len(sys.argv[1:])
        if argc < 1:
            self.mode = 'help'
        else:
            self.mode = 'run'
        
        i = 1
        while (i <= argc):
            if argv[i].strip() == "-a":
                self.mode = 'all'
            i += 1


    def read_job_db(self):
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
        
        return np.vstack([dirnames, job_idx, times])

    def find_last_job(self, dirname):
        """
        Return the highest job index from outfiles in the directory `dirname`.
        """
        filelist = glob.glob(os.path.join(dirname, "*.out"))
        job_id_list = [int(name.split('.')[0].split('-')[1]) for name in filelist]

        return max(job_id_list) if len(job_id_list) > 0 else None
    
    def check_accounting(self, job_id):
        pass

    def check_squeue(self, job_id):
        pass
    
    def check_outfile(self, job_id):
        pass

    def execute(self, job_idx, params, dirname):
        idx = np.where(self.db[0] == dirname)[0]
        job_id = self.db[1, idx]

        status = self.check_accounting(job_id)

        sep = " "*4
        print("{job_id}{sep}{parameters}{sep}{dirname}{sep}{status}".format(job_id=job_id, sep=sep, parameters=params, dirname=dirname,status=status))

class DataProcessor(ParameterIterator):
    pass

    def process(self):
        """
        Overload this function to do some processing.
        """
        pass

def setup_default_settings():
    """
    Setup the default settings dictionary.
    """
    settings = dict()
    settings.update([['script_path', './slurm.sh']])
    settings.update([['config_path', 'config.ini']])
    settings.update([['submit_as', 'sbatch']])
    settings.update([['overwrite_dir', False]])
    settings.update([['test_mode', True]])
    settings.update([['jobname_prefix', '']])
    settings.update([['logfile_name', 'slurm.log']])

    return settings

def get_wildcard(name):
    """
    Create a wildcard of the form `<NAME>_VAL` from name.
    This is supposed to ensure that when replacing the wildcard in the bash script,
    no accidental mismatch occurs.
    """
    return name.upper() + "_VAL"

def get_mode(argv):
    pass
    argc = len(sys.argv[1:])
    if argc < 1:
        mode = 'help'
    else:
        mode = 'run'
    
    supdate = dict()

    num_set = [] # list of numbers set

    i = 1
    while (i <= argc):
        
        if argv[i].strip() == "-f":
            if argc >= i+1:
                supdate.update([['config_path', argv[i+1]]])
            else:
                raise ConfigPathError
            i += 2
        elif argv[i].strip() == '-F':
            mode = 'printini'
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
                pass
                raise
            num_set.append(num)
        i += 1
    
    if len(num_set) == 1:
        supdate.update([['start_index', 1]])
        supdate.update([['num_submits', num_set[0]]])
    elif len(num_set) > 1:
        supdate.update([['start_index', num_set[0]]])
        supdate.update([['num_submits', num_set[1]]])

    if mode == 'run':
        return True, supdate
    elif mode == 'help':
        return False, None
    elif mode == 'printini':
        return False, supdate
    else:
        return False, None

def get_underline(str):
    """
    Return an underline string of the same length as `str`.
    """
    return "="*len(str) + "\n"

def display_help():
    """
    Display welcome screen and help message in the console.
    """
    pass
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

def copy_default_ini(dst):
    path = os.path.dirname(os.path.realpath(__file__))
    shutil.copy(os.path.join(path, 'ini', 'config.ini'), dst)

def submit_sbatch(filename):
    
    p = subprocess.Popen(["sbatch", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out_str, err_str = p.communicate()
    return out_str

def submit_srun():
    pass

def get_wildcard_list(params):
    wildcard_list = []
    for name in params.get_names():
        wildcard_list.append(get_wildcard(name))
    wildcard_list.append("JOBNAME")
    return wildcard_list

def get_submit_msg(dname_vals, format_str):
    
    format_ids = format_str.split("_")
    submit_strs = ["{name}={id}, ".format(name=name, id=format_ids[i]) for i,name in enumerate(dname_vals)]
    submit_str = ""
    for sstr in submit_strs:
        submit_str += sstr
    if len(submit_str) > 0:
        submit_str = submit_str[:-2]
    
    return submit_str



def do_submit():
    pass

def main(mode=None, argv=['name']):
    """
    Perform the main duties of the program.
    The mode parameter decides which functionality is executed.

    mode    : either 'submit' or 'status'
    """
    if mode is None:
        sys.exit()
    elif mode is 'submit':
        func = do_submit
    elif mode is 'status':
        func = do_status
    else:
        sys.exit()
    
    lacommon.assert_dir(db_dir)

    try:
        retval, supdate = get_mode(argv)
    except ConfigPathError:
        sys.stdout.write('Error! No config file path specified!\n')
        sys.exit()

    if not retval:
        if supdate is None:
            # help mode
            display_help()
        elif 'ini_dst' in supdate:
            # copy default ini file to destination
            copy_default_ini(supdate.get('ini_dst'))
    else:
        pass
        # run program

        settings = setup_default_settings()

        # update default settings with command line input
        settings.update(supdate)

        # get settings from config file
        try:
            params, f_settings = ini.parameters_from_ini(settings.get('config_path'))
        except ini.IniFormatError as e:
            sys.stdout.write('Error! Wrong format in config file.\n')
            sys.stdout.write(str(e) + '\n')
        except IOError:
            sys.stdout.write('Error! Could not read file `{}`.\n'.format(settings.get('config_path')))
            sys.exit()
        except TypeError:
            sys.stdout.write('Error! Could not read file `{}`.\n'.format(settings.get('config_path')))
            sys.exit()
        except:
            raise
        
        # fix formatting of parameters
        if 'par_in_dirname' in f_settings:
            f_settings.update([['par_in_dirname', [v.strip() for v in f_settings['par_in_dirname'].split(',')]]])
        
        # update default settings with ini file settings and command line input settings
        # command line options are favored
        settings.update(f_settings)
        settings.update(supdate)

        # setup logger
        logging.basicConfig(filename=settings.get('logfile_name'), level=logging.INFO)

        # make sure setting `par_in_dirname` is set
        if not 'par_in_dirname' in settings:
            settings.update([['par_in_dirname', params.get_names()]])
        assert common.list_prod([p in params.get_names() for p in settings.get('par_in_dirname')])
        
        if lacommon.fexists('slurm.log'):
            # print a separation line
            logging.info('\n\n' + '='*80 + "\n")
        
        tot_num_jobs = params.get_maxnum()

        jobs = Jobs()

        start_job = settings['start_index']
        num_jobs = settings['num_submits']

        last_job = start_job + num_jobs -1
        if last_job > tot_num_jobs:
            last_job = tot_num_jobs
            num_jobs = last_job - start_job + 1
            logging.info("Number of jobs larger than available jobs. Overriding with: %s" % num_jobs)

        logging.info("Submitting jobs %(start)d - %(stop)d / %(tot)d\n" % \
                {'start' : start_job, 'stop' : last_job,
                'tot' : tot_num_jobs})
        
        first_job = start_job -1

        num_dname_vals = len(settings['par_in_dirname'])
        dtypes = [ type(params.get_values_ax(name)[0]) for name in settings['par_in_dirname']]
        decimals = None
        format_str = lacommon.generate_format_spec(num_dname_vals, "_", dtypes, decimals)

        wildcard_list = get_wildcard_list(params)

        for job_idx, pj in enumerate(params[first_job:first_job + num_jobs]):
            cur_dname_vals = [str(pj[params.get_axis(name)]) for name in settings['par_in_dirname']]
            cur_vals = [str(val) for val in pj]
            
            submit_str = get_submit_msg(settings['par_in_dirname'], format_str)

            dir_name = format_str.format(*cur_dname_vals)
            existed = lacommon.assert_dir(dir_name)
            
            if existed and (not settings['overwrite_dir']):
                # skip existing directories if `overwrite_dir` is disabled
                logging.warning("Skipping " + submit_str.format(*cur_dname_vals) + ", directory existed. \
                Change setting `overwrite_dir` if you want to write in existing directories.")
            else:
                
                jobname = settings.get('jobname_prefix') + dir_name

                cur_vals += [jobname]

                filename = os.path.basename(settings.get('script_path'))

                lacommon.copy_replace(settings.get('script_path'), os.path.join(dir_name, filename), wildcard_list, cur_vals)


                #logging.info("Submitting job for U=%(U).2f, lambda=%(lambda).2f, gamma=%(gamma).2f" \
                #            % {'lambda' : cur_lambda, 'U': cur_U, 'gamma' : cur_gamma})
                logging.info("Submitting job for " + submit_str.format(*cur_dname_vals))

                os.chdir(dir_name)

                if not settings['test_mode']:
                    try:
                        if settings.get('submit_as').lower() == 'sbatch':
                            out_str = submit_sbatch(filename)
                        elif settings.get('submit_as').lower() == 'srun':
                            raise NotImplementedError
                        else:
                            raise NotImplementedError
                        logging.info(out_str)
                        if "ERROR" not in out_str.upper() and "FAILED" not in out_str.upper():
                            jobs.success()
                    except:
                        logging.warning("Submission failed.")
                else:
                    logging.info("Test mode active. Not submitting.")
                    jobs.success()

                os.chdir("../")
        
        assert jobs.get_total() == num_jobs

        if jobs.get_success() < num_jobs:
            last_job = start_job + jobs.get_success() - 1

        if last_job < tot_num_jobs:
            logging.info("\nSubmission complete.\nSuccess: {}/{}\nNext job: {} of {}".format(jobs.get_success(), jobs.get_total(), (last_job + 1), tot_num_jobs))
        else:
            logging.info("\nSubmission complete. All %d jobs submitted." % tot_num_jobs)




"""
if False:

    params, settings = ini.parameters_from_ini('./TI_config.ini')

    if 'filling' in settings:
        filling = settings.get('filling')
    else:
        filling = 1.
    if 'maxiters' in settings:
        maxiters = settings.get('maxiters')
    else:
        maxiters = 15

    # parameters to include in directory names
    if 'par_in_dirname' in settings:
        dname_vals = settings['par_in_dirname'].split(',').strip()
    else:
        dname_vals = params.get_names()

    incl = [v in params.get_names() for v in dname_vals]
    not_incl = []
    for i,v in enumerate(dname_vals):
        if not v:
            not_incl.append(dname_vals[i])
        
    if len(not_incl) > 0:
        error_str = ""
        for n in dname_vals:
            error_str += n + ", "
        error_str = error_str[:-2]
        raise Exception("Parameter name(s) {} not defined.".format(error_str))

    num_dname_vals = len(dname_vals)
    dtypes = [ type(params.get_values_ax(name)[0]) for name in dname_vals]
    #decimals = [ lacommon.find_max_num_decimals(params.get_values_ax(name)) for name in dname_vals]
    decimals = None
    format_str = lacommon.generate_format_spec(num_dname_vals, "_", dtypes, decimals)
    format_ids = format_str.split("_")
    submit_strs = ["{name}={id}, ".format(name=name, id=format_ids[i]) for i,name in enumerate(dname_vals)]
    submit_str = ""
    for sstr in submit_strs:
        submit_str += sstr
    if len(submit_str) > 0:
        submit_str = submit_str[:-2]


    # write in existing directories?
    if 'overwrite_dir' in settings:
        settings['overwrite_dir'] = lacommon.str_to_bool(settings.get('overwrite_dir'))
    else:
        settings.update([['overwrite_dir', False]])

    if 'script_path' not in settings:
        settings.update([['script_path', os.path.expanduser("~/CODES/scripts/slurm.sh")]])

    wildcard_list = []
    for name in params.get_names():
        wildcard_list.append(get_wildcard(name))
    wildcard_list.append("JOBNAME")
    wildcard_list.append("FILLING_VAL")
    wildcard_list.append("MAXITERS_VAL")


    if len(sys.argv) > 2:
        start_job = int(sys.argv[1])
        num_jobs = int(sys.argv[2])
        assert start_job > 0, "First job index must be >0."
    else:
        start_job = 1
        num_jobs = int(sys.argv[1])
    assert num_jobs > 0, "Number of jobs must be positive."

    for i,arg in enumerate(sys.argv):
        if arg == "filling" and len(sys.argv) > i+1:
            filling = sys.argv[i+1].split('/')
            try:
                if len(filling) > 1:
                    filling = float(filling[0]) / float(filling[1])
                else:
                    filling = float(filling[0])
            except:
                try:
                    filling = float(filling)
                except:
                    raise


    logging.info("")

    tot_num_jobs = params.get_maxnum()
    last_job = start_job + num_jobs -1
    if last_job > tot_num_jobs:
        last_job = tot_num_jobs
        num_jobs = last_job - start_job + 1
        logging.info("Override number of jobs: %s" % num_jobs)

    logging.info("Submitting jobs %(start)d - %(stop)d / %(tot)d" % \
            {'start' : start_job, 'stop' : last_job,
            'tot' : tot_num_jobs})
    num_success = 0
    first_job = start_job -1
    for job_idx, pj in enumerate(params[first_job:first_job + num_jobs]):
        #U_idx = job_idx % U_num
        #lambda_idx = (job_idx // U_num ) % lambda_num
        #gamma_idx = job_idx // (U_num * lambda_num)
        
        #cur_lambda = pj[params.get_axis('lambda')] #lambda_x[lambda_idx]
        #cur_U = pj[params.get_axis('U')] #U[U_idx]
        #cur_gamma = pj[params.get_axis('gamma')] #gamma[gamma_idx]
        cur_dname_vals = [str(pj[params.get_axis(name)]) for name in dname_vals]
        cur_vals = [str(val) for val in pj]
        
        #dir_name = "{}_{}_{}".format(cur_gamma, cur_lambda, cur_U)
        dir_name = format_str.format(*cur_dname_vals)
        existed = lacommon.assert_dir(dir_name)
        skip_this = False
        if existed and not settings['overwrite_dir']:
            skip_this = True
            logging.warning("Skipping " + submit_str.format(*cur_dname_vals) + ", directory existed. \
            Change setting `overwrite_dir` if you want to write in existing directories.")
        else:
            filename = "slurm.sh"
            #filepath = os.path.expanduser("~/CODES/scripts/slurm.sh")
            filepath = settings.get('script_path')
            jobname = "TI"+dir_name

            cur_vals += [jobname, filling, maxiters]

            #lacommon.copy_replace(filepath, os.path.join(dir_name, filename), \
            #            ["GAMMA_VAL", "LAMBDA_VAL", "U_VAL", "JOBNAME", "FILLING_VAL"], \
            #            [str(cur_gamma), str(cur_lambda), str(cur_U), jobname, str(filling)])
            lacommon.copy_replace(filepath, os.path.join(dir_name, filename), wildcard_list, cur_vals)


            #logging.info("Submitting job for U=%(U).2f, lambda=%(lambda).2f, gamma=%(gamma).2f" \
            #            % {'lambda' : cur_lambda, 'U': cur_U, 'gamma' : cur_gamma})
            logging.info("Submitting job for " + submit_str.format(*cur_dname_vals))

            os.chdir(dir_name)

            if not TEST_MODE:
                try:
                    #out_str = subprocess.check_output(["sbatch", filename])
                    p = subprocess.Popen(["sbatch", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    out_str, err_str = p.communicate()
                    logging.info(out_str)
                    if "ERROR" not in out_str.upper() and "FAILED" not in out_str.upper():        
                        num_success += 1
                except:
                    logging.info("Submission failed.")
            else:
                logging.info("Test mode active. Not submitting.")
                num_success += 1

            os.chdir("../")
    if num_success < num_jobs:
        last_job = start_job + num_success - 1

    if last_job < tot_num_jobs:
        logging.info("Submission complete. Next job: %d" % (last_job + 1) +
            " of %d" % (tot_num_jobs))
    else:
        logging.info("Submission complete. All %d jobs submitted." % tot_num_jobs)
"""