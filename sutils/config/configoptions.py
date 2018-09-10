from ..configparse import configparse
from ..configparse import cfgtypes
from ..slurm_interface.config import TimeType as SlurmTimeType


# these are general settings for the submission and directory management
general_group = configparse.ConfigSection('general') \
                .add_option('script_path', cfgtypes.PathType, 'slurm.sh') \
                .add_option('par_in_dirname', cfgtypes.StringListType, []) \
                .add_option('overwrite_dir', cfgtypes.BoolType, False) \
                .add_option('submit_as', cfgtypes.StringType, 'sbatch') \
                .add_option('cmd_arguments', cfgtypes.StringType, '') \
                .add_option('jobname_prefix', cfgtypes.StringType, 'j') \
                .add_option('logfile_name', cfgtypes.StringType, 'ssubmit.log') \
                .add_option('write_parameter_info', cfgtypes.BoolType, 'True') \
                .add_option('test_mode', cfgtypes.BoolType, True) \
                .add_option('dirname_prefix', cfgtypes.StringType, '')


# these are settings for the parameters instance
pconfig_group = configparse.ConfigSection('pconfig') \
                .add_option('mode', cfgtypes.StringType, 'square') \
                .add_option('maxdecimals', cfgtypes.IntType, 3)


# these are settings for SBATCH
# NOTE these should probably defined in slurm_interface.config
slurm_group = configparse.ConfigSection('sbatch') \
                .add_option('manual', cfgtypes.BoolType, True) \
                .add_option('partition', cfgtypes.StringType, 'test') \
                .add_option('time', SlurmTimeType, '0-00:05:00') \
                .add_option('ntasks', cfgtypes.IntType, 1) \
                .add_option('cpus-per-task', cfgtypes.IntType, 1) \
                .add_option('mem-per-cpu', cfgtypes.IntType, 2000) \
                .add_option('mem', cfgtypes.IntType, 2000) \
                .add_option('mail-type', cfgtypes.StringListType, ['FAIL'])


# these are generic parameter settings
# param_value_group = configparse.ConfigSection('parameter-scalar') \
#                 .add_option('name', cfgtypes.StringType, '', required=True)
# value_values_group = param_value_group.add_mutually_exclusive_group(required=True) \
#                 .add_option('value', cfgtypes.StringType) \
#                 .add_option('values', cfgtypes.StringListType)


# param_range_group = configparse.ConfigSection('parameter-range', required=False) \
#                 .add_option('name', cfgtypes.StringType, '', required=True) \
#                 .add_option('lo', cfgtypes.RealType, required=True) \
#                 .add_option('hi', cfgtypes.RealType, required=True)
# step_points_group = param_step_group.add_mutually_exclusive_group(required=True) \
#                 .add_option('step', cfgtypes.RealType) \
#                 .add_option('points', cfgtypes.RealType)


# param_vector_group = configparse.ConfigSection('parameter-vector', required=False) \
#                 .add_option('name', cfgtypes.StringType, '', required=True)
# vector_vectors_group = param_vector_group.add_mutually_exclusive_group(required=True) \
#                 .add_option('value', cfgtypes.StringType) \
#                 .add_option('values', cfgtypes.StringVectorListType)


# parser
parser = configparse.ConfigParser() \
                .add_section(general_group) \
                .add_section(pconfig_group) \
                .add_section(slurm_group)
                #.add_section(param_value_group) \
                #.add_section(param_range_group) \
                #.add_section(param_vector_group)
