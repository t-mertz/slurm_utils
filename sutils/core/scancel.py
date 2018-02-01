import subprocess
import sys
import os
import pwd

CATCH_EXCEPTIONS = True

def process_input(argv):
    """
    Process the argument list and determine execution mode.
    """
    remaining = len(argv[1:])

    if remaining == 0:
        print("Must specify a job ID or a number of jobs to be cancelled (options -l, -f).")
        sys.exit(0)
    i = 1 
    if remaining > 0:
        arg = argv[i]
        if arg.strip() == "-l":
            mode = "last"
            try:
                num = int(argv[i+1])
            except TypeError:
                if CATCH_EXCEPTIONS:
                    print("Input must be integer.")
                else:
                    raise TypeError("Input must be integer.")
            i += 2
        elif arg.strip() == "-f":
            mode = "first"
            try:
                num = int(argv[i+1])
            except TypeError:
                if CATCH_EXCEPTIONS:
                    print("Input must be integer.")
                else:
                    raise TypeError("Input must be integer.")
            i += 2
        else:
            mode = "ind"
            try:
                num = int(argv[i])
            except TypeError:
                if CATCH_EXCEPTIONS:
                    print("Input must be integer.")
                else:
                    raise TypeError("Input must be integer.")
            i += 1
    else:
        print("Unexpected error: No arguments.")
        sys.exit(1)
    
    return mode, num

def cancel(mode, num):

    if mode == "ind":
        subprocess.call(["scancel", str(num)])
    
    else:
        username = pwd.getpwuid(os.getuid())[0]

        args = "squeue | grep {}".format(username)
        args = "squeue -u {}".format(username)

        proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

        # get a list of all currently running jobs for the current user
        jobs = []

        for i,l in enumerate(proc.stdout):
            #print l
            if i > 0:
                jobs.append(l.split()[0])

        jobs = sorted(jobs)
        njobs = len(jobs)

        if njobs > 0:
            print("Found {} jobs: ".format(njobs) + ", ".join(jobs))
        else:
            print("No jobs found")
            sys.exit(0)

        if mode == "last":
            if num > njobs:
                minn = None
            else:
                minn = max(-1, njobs-1 - num)

            # cancel jobs from `minn+1` to the last
            for j in jobs[-1:minn:-1]:
                sys.stdout.write(j)
                subprocess.call(["scancel", str(j)])
                sys.stdout.write(" cancelled\n")
        elif mode == "first":
            if num > njobs:
                num = None
            
            # cancel jobs from 0 to `num`
            print("Cancelling jobs:")
            for j in jobs[:num]:
                sys.stdout.write(j)
                subprocess.call(["scancel", str(j)])
                sys.stdout.write(" cancelled\n")


def main(argv):
    
    # get mode
    # WARNING: at the moment only one option is allowed!
    mode, num = process_input(argv)

    cancel(mode, num)
