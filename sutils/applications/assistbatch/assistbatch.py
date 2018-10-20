from ...slurm_interface import api as slurm
from ...slurm_interface import resources


def run(options):
    hwdata = slurm.sinfo_detail()

    # get requested cores and nodes from bash script
    ncpus = None
    nnodes = None
    partition = None

    # filter partition!
    part_hwdata = hwdata.filter_partition(partition)

    # get optimal resource allocation (just idle)
    opt = resources.find_resources(part_hwdata, ncpus, idle=True)

    if opt is not None:
        opt_ncpus, opt_nnodes = opt

        if opt_ncpus != ncpus:
            # query user to accept change
            pass
        if nnodes is not None and nnodes > opt_nnodes:
            # query user if this was intentional
            pass
    else:
        # query user if queueing is ok

        # look again for all CPUs
        opt = resources.find_resources(part_hwdata, ncpus, idle=False)

        if opt is None:
            print("Error: Number of requested cores exceeds total number of "\
                    +"partition {}. \nAborting.".format(partition))
        else:
            opt_ncpus, opt_nnodes = opt

            if opt_ncpus != ncpus:
                # query user to accept change
                pass
            if nnodes is not None and nnodes > opt_nnodes:
                # query user if this was intentional
                pass

