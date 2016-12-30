"""
    == ParameterLib ==
    
    parameters.py, this module implements the `Parameter` and `Parameters` classes.

    Author:     Thomas Mertz
    Copyright:  (c) 2016, Thomas Mertz
    License:    GNU General Public License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED 
    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
    IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
    OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
    WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
    OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
    ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


    **DESCRIPTION**:

    These data types can be used to efficiently handle sets of parameters, since
    the iteration over all combination and conversion to a one-dimensional
    index is implemented.
    This can reduce user code a lot, since after construction only method calls
    are necessary.

    With `Parameters`, values can be retrieved by name or index, parameter combinations 
    can be transformed into a scalar index and the other way around.
    The class also implements an iterable, so that one can easily iterate over an instance,
    where the tuple of the current combination will be returned.
"""

import numpy as np
import common
try:
    import cPickle
    PICKLED = True
except:
    PICKLED = False

prod = common.list_prod # alias list product

DEBUG = False

class ParameterNotFoundError(Exception):
    """
    Raised if a specified parameter name could not be found.
    """
    def __init__(self, value=''):
        self._value = value
        
    def __str__(self):
        return repr(self._value)

class ParameterNotUniqueError(Exception):
    """
    Raised if a specified parameter value appears more than once.
    """
    def __init__(self, value=''):
        self._value = value
        
    def __str__(self):
        return repr(self._value)

class EmptyParameterError(Exception):
    """
    Raised if an empty Parameter or Parameters instance is
    initialized.
    """
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return 'Number of values must be >0, is {}'.format(self._value)

class Parameter(object):
    """
    Defines a generic data type for parameters, containing a name and a range
    of values the parameter can take.
    """
    def __init__(self, name, values):
        pass
        self._name = name
        self._values = values
        self._dim = len(values)
        if self._dim < 1:
            raise EmptyParameterError(self._dim)
        
    def get_name(self):
        """
        Return the parameter name.
        """
        return self._name

    def get_values(self):
        """
        Return the range of values.
        """
        return self._values
        
    def get_dim(self):
        """
        Return the number of values.
        """
        return self._dim


class Parameters(object):
    """
    Defines a data type Parameters, which stores the values and names of the
    parameters used and provides methods for conversion to integer.
    
    The unique integer representant can then be used to reference a specific
    parameter combination. 
    """

    modes = ['square',
             'irregular']

    def __init__(self, parameters, mode='square', order='r'):
        """
        Constructor for the Parameters class.
        
        ----------------------------------------------
        
        Parameters:
        
        parameters   :  iterable containing Parameter instances or numpy arrays
        mode         :  details whether or not parameters are defined on a square
                        grid.
                        'square' (default)
                        'irregular'
        order        :  set storage order of parameters
                        'r': row-major order (default)
                        'c': column-major order
                        
        """
        pass
        self._dim = len(parameters) # number of parameters
        assert mode.lower().strip() in Parameters.modes, "Invalid mode: %s" % mode

        if mode == 'square':
            if type(parameters[0]) == Parameter:
                self._axis_dim = [p.get_dim() for p in parameters]
                self._parameters = parameters
                self._values = [self._parameters[i].get_values() for i in range(self._dim)]
                self._names = [p.get_name() for p in parameters]
            
            else:
                try:
                    self._names = [p[0] for p in parameters] # names per axis
                    self._values = [p[1] for p in parameters] # values per axis
                    self._axis_dim = [len(p) for p in self._values] # dimensions per axis
                except:
                    raise
            self._maxnum = prod(self._axis_dim) # number of different parameter combinations
            if self._maxnum < 1:
                raise EmptyParameterError(self._maxnum)
            
        elif mode == 'irregular':
            self._values = parameters['values']
            self._parameters = parameters['names']
                
    def get_dim(self):
        """
        Getter method. Get number of different parameters in the Parameters tuple.
        
        Example:
        An instance represented by 'a | b' has dimension 2.
        """
        return self._dim
    
    def get_maxnum(self):
        """
        Getter method. Get number of different parameter combinations,
        i.e. the largest integer (+1) index.
        """
        return self._maxnum
    
    def get_types(self):
        """
        Getter method. Get types of all parameters.
        """
        return [type(v[0]) for v in self._values]

    def get_name(self, axis):
        """
        Return the name of the parameter corresponding to the specified 
        axis.
        
        ----------------------------------------------------------
        
        Parameters:
        
        axis  :  int, number of parameter
        """
        
        if hasattr(self, '_names'):
            return self._names[axis]
        else:
            try:
                return self._parameters[axis].get_name()
            except:
                raise
    
    def get_names(self):
        return self._names
    
    def get_number(self, values):
        """
        Return the unique integer representation for the values specified.
        Values have to be specified by axis, i.e. as an iterable data type
        with as many components as there are axes.
        
        At the moment this only works for 'quadratic' types.
        
        ------------------------------------------------------------
        
        Parameters:
        
        values  :  iterable, contains parameter values of the sought-after
                   representant
        """ 
        pass
        try:
            assert hasattr(values, '__iter__'), "Input not iterable"
        except TypeError:
            raise
        except ValueError:
            raise

        viter = []
        
        for i,v in enumerate(values):
            if hasattr(v, '__iter__'):
                assert hasattr(self._values[i][0], '__iter__'), "Iterable argument for non-iterable parameter given."
                assert len(v) == len(self._values[i][0]), "Input length does not match parameter length for axis %d." % i
                viter.append(True)
            else:
                assert not hasattr(self._values[i][0], '__iter__'), "Non-iterable argument for iterable parameter given."
                viter.append(False)

        idx = []
        i = 0
        check = True
        for v in values:
            if viter[i]:
                this_idx = np.where( (self._values[i] == v).all(axis=1))[0]
            else:
                this_idx = np.where(self._values[i] == v)[0]
            
            check *= len(this_idx) != 0
            if len(this_idx) > 1:
                raise ParameterNotUniqueError("Parameter number {}: {}, is not unique!".format(i, v))
            if check:
                idx += [int(this_idx)]
            else:
                break
            if DEBUG:
                print(this_idx, idx)
            #check *= v in self._parameters[i].get_values()
            i += 1
        
        if check:
            tmp = [idx[i]* prod(self._axis_dim[i+1:]) for i in range(self._dim)]
            int_idx = int(sum(tmp))
            assert int_idx < self._maxnum
            return int(sum(tmp))
        else:
            raise ParameterNotFoundError(values)

    def search(self, parameters):
        """
        Search for parameters and return hits.
        
        Parameters:
        parameters      : (iterable) list of name, value pairs, e.g. [[name1,value1],...]
        """
        values = [None] * self._dim
        for p in parameters:
            values[self.get_axis(p[0])] = p[1]
        
        return values
    
    def get_values_ax(self, name):
        """
        Return all values corresponding to `name`.

        `name` can be integer (axis) or string.
        """
        try:
            name = int(name)
            return self._values[name]
        except:
            if name in self.get_names():
                ax = self.get_axis(name)
                return self._values[ax]
            else:
                return []
            
    
    def get_values(self, number):
        """
        Return the values corresponding to the integer representation
        number.
        
        ---------------------------------------------------------
        
        Parameters:
        
        number  :  int, representant for parameter set
        """
        pass
        assert number < self._maxnum
        
        # create index list for every axis.
        idx = []
        for d in range(self._dim-1):
            #print(self._axis_dim[d:])
            dim_prod = prod(self._axis_dim[d+1:]) # product of dimensions
            idx += [number // dim_prod]
            number = number % dim_prod
        idx += [number]
        
        values = [self._values[i][idx[i]] for i in range(self._dim)]
        
        return values
        
    def get_number_list(self):
        """
        Return list of all integer representants.
        Used for iterating over all parameters.
        """
        return list(range(self._maxnum))
    
    def get_axis(self, string):
        """
        Return the integer axis of the parameter named 'string'.
        
        Raises 'ParameterNotFoundError' if no match is found.
        """
        i = 0
        while i < self._dim:
            if self._names[i] == string:
                return i
            i += 1
        
        raise ParameterNotFoundError(string)
        
    def __repr__(self):
        out_str = ""
        if hasattr(self, '_names'):
            for n in self._names[:-1]:
                out_str += n + " | "
            out_str += self._names[-1]
        else:
            for n in self._parameters[:-1]:
                out_str += n.get_name() + " | "
            out_str += self._parameters[-1].get_name()
        out_str += "\n"
        for i in self.get_number_list():
            out_str += str(self.get_values(i)) + "\n"
        return out_str     

    def to_file(self, filename):
        """
        Save the Parameters instance to a file.
        
        Interfaces cPickle for user convenience.
        """
        if PICKLED:
            cPickle.dump(self, open(filename, 'wb'))
        
    def add(self, parameters, index=None):
        """
        Add another parameter to an existing instance.
        
        Parameters:
        parameter       : (iterable) new parameters in list of [name, value] pairs
                          e.g. [[name1, values1],...]
        index           : (int) index before which the new parameter should be placed
                          defaults to None, where the new parameter will be appended
        """
        self._dim += len(parameters)
        for p in parameters:
            self._names.insert(index, p[0])
            self._values.insert(index, p[1])
            self._axis_dim.insert(index, len(p[1]))
        self._maxnum = prod(self._axis_dim)
    
    def __iter__(self):
        for i in range(self._maxnum):
            yield self.get_values(i)

    def __getitem__(self, slice):
        vlist = []
        for i in self.get_number_list()[slice]:
            vlist.append(self.get_values(i))
        return vlist

    def __len__(self):
        return self._maxnum

def load(filename):
    """
    Load Parameters instance from file.
    
    Interfaces cPickle for user convenience.
    """
    if PICKLED:
        cPickle.load(open('filename', 'rb'))