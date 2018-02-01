# -*- coding: utf-8 -*-
"""
	== ParameterLib, EasyMP, Progress ==
	
    lacommon.py, Implements several common functions used throughout other 
    parts of the program.

    Author:     Thomas Mertz
    Copyright:  (c) 2015-2016, Thomas Mertz
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
"""

from __future__ import division
import numpy as np
import math
import os

factorial = math.factorial

def sign(x):
	#return x/abs(x)
	return 1 if x>=0 else -1

def pfaff(A):
	
	pass
	assert len(A.shape) == 2
	assert A.shape[0] == A.shape[1]
	
	dim = A.shape[0]
	
	if dim % 2 != 0:
		return 0
	
	pf_A = 0
	
	dims = [dim-i for i in xrange(0,dim)]
	
	#for p in np.ndindex(*((dim,)*dim)):
	for n in np.ndindex(*dims):
		ind = range(dim)
		p = []
		
		for i in xrange(dim):
			p.append(ind.pop(n[i]))
			
		N = 0
		for i in xrange(dim):
			for j in xrange(i+1,dim):
				if p[i] > p[j]:
					N += 1
				else:
					pass
		sgn_p = (-1)**N
		
		# beware: mathematical indices
		i_odd = range(0,dim,2)
		i_even = range(1,dim+1,2)
		
		p1 = np.asarray(p)
		
		prod_p = A[p1[i_odd],p1[i_even]].prod()
		
		#print(prod_p)
		if False:
			if prod_p != 0:
				print(p)
				
		if False:
			print((p,sgn_p))
		
		pf_A += sgn_p * prod_p
	
	pf_A /= 2**(dim/2) * factorial(dim/2)
	
	return pf_A
	
def rand_skew_symm_mat(dim=2,cmplx=False):
	import numpy.random as rnd
	
	A = rnd.random([dim,dim])
	if cmplx:
		B = rnd.random([dim,dim])
		
		A = A + 1j * B
	
	return A - A.transpose()
	
def test_pfaff(dim=2,num=10,accuracy=1e-5):
	part = "-"*10
	log_txt = "Testing...\n\n{3}\n\ndim {0}\nnum {1}\nacc {2}\n\n{3}\n".format(dim,num,accuracy,part)
	print(log_txt)
	for i in xrange(num):
		A = rand_skew_symm_mat(dim,cmplx=True)
		if abs(np.linalg.det(A) - pfaff(A)**2) > accuracy:
			print("Test failed!")
			return 1
	print("Test successful!")
	return 0
	
def linear_interp(f,x,x_eval):
	# return the function value f(x_eval) by connecting the two points given

	assert len(f) == len(x) == 2
	assert x[0] != x[1]
	m = (f[1] - f[0]) / (x[1] - x[0])
	
	return x[0] + m * (x_eval - x[0])
	
def ishermitian(A):
	return True if (A == A.transpose().conjugate()).all() else False
	
def poly_interp(f,x,x_eval):
	pass
	
def format_time(t, format_spec='dhms'):
	"""
	Return a formatted time string describing the duration of 
	the input in seconds in terms of days,hours,minutes and seconds.
	"""
	if format_spec == '':
		sb, mb, hb, db = True, True, True, True
	else:
		sb = 's' in format_spec
		mb = 'm' in format_spec
		hb = 'h' in format_spec
		db = 'd' in format_spec
	
	t = round(t, 2)
	if t >= 60 and (mb or hb or db):
		m = t // 60
		s = t - m*60
		if m >= 60 and (hb or db):
			h = m // 60
			m = m - h*60
			if h >= 24 and db:
				d = h // 24
				h = h - d*24
			else:
				d = 0
		else:
			h,d = 0,0
	else:
		s = t
		m,h,d = 0,0,0
	
	time_str = ""
	#if format_spec == 's':
	#	time_str += "{}s".format(t)
	if format_spec == '':
		db = not d == 0
		hb = not h == 0
		mb = not m == 0
		sb = not s == 0
	if not (db or hb or mb or sb):
		sb = True
		
	if db:
		time_str += "{:.0f}d ".format(d)
	if hb:
		time_str += "{:.0f}h ".format(h)
	if mb:
		time_str += "{:.0f}m ".format(m)
	if sb:
		time_str += "{:0=4.1f}s".format(s)
	#return "{}d {}h {}m {}s".format(d,h,m,s)
	return time_str

def assert_dir(path):
	"""
	Check if a path exists, if not create a directory.

	If path existed before, return True, else False.
	"""
	existed = False
	if not os.access(path, os.F_OK):
		os.mkdir(path)
	else:
		existed = True
	
	return existed
	
	
def fexists(path):
	"""
	Check if a path exists.
	"""
	if os.access(path, os.F_OK):
		return True
	return False

def funiquename(path, extension=""):
	"""
	Create a unique filename by appending a number separated by an underscore
	to the end of the existing filename. The first match is returned.
	
	If extension is supplied, it will be appended at the end of the filename.
	"""
	def extend(p, e):
		return p + e
	
	if fexists(extend(path, extension)):
		i = 1
		while fexists(extend(path+"_{}".format(i),extension)):
			i += 1
		return extend(path + "_{}".format(i), extension)
	return extend(path, extension)
		
def isiterable(var):
	"""
	Check if input is iterable.
	"""
	return hasattr(var, "__iter__")

def isdirectory(path):
    """
    Check if input path is a directory.
    """
    try:
        os.chdir(path)
        os.chdir('..')
    except OSError:
        return False

    return True

def listdirs(path):
    """
    List only directories one level lower than path in the directory tree.
    """
    filelist = os.listdir(path)

    dirlist = []
    for fname in filelist:
        if isdirectory(os.path.join(path, fname)):
            dirlist.append(fname)

    return dirlist

def copy_replace(in_path, out_path, pattern, subst):
	"""
	Replace all occurrences of `pattern` in file `in_path` by `subst` and
	save the copy to `out_path`.
	`pattern` and `subst` can be iterable.
	"""
	if hasattr(pattern, '__iter__'):
		iter = True
		num_patterns = len(pattern)
	else: iter = False
	
	if not iter:
		with open(in_path, 'r') as input_file:
			with open(out_path, 'w') as output_file:
				for line in input_file:
					output_file.write(line.replace(pattern, subst))
	
	else:
		with open(in_path, 'r') as input_file:
			with open(out_path, 'w') as output_file:
				for line in input_file:
					replace_itms = 0
					pattern_itm = pattern[0]
					subst_itm = subst[0]
					for p,s in zip(pattern, subst):
						if p in line:
							replace_itms += 1
							pattern_itm = p
							subst_itm = s
					if replace_itms > 1:
						raise RuntimeError("Warning possible conflict!")
					output_file.write(line.replace(pattern_itm, subst_itm))

def generate_format_spec(num_vals, sep, dtypes, decimals=None):
    """
    Generate a format specifier for generic input.
    
    --------------------------------------------------------------
    
    Input
    
    num_vals : number of wild-cards
    sep      : separator string (could be '_', '-', '--' ...)
               used to separate wild-cards
    dtypes   : data types of the wildcards ('str', 'float', 'int')
    decimals : number of decimals (only relevant for floats)
    
    --------------------------------------------------------------
    
    Output
    
    String of the form: "{0:<dtype>}<sep>{1:<dtype>}<sep>...",
    where each occurrence of <dtype> is replaced by the dtype value of
    the current wild-card and <sep> is replaced by the separator string. 
    """
    assert type(num_vals) is int
    
    # dictionary of identifiers for supported data types
    dident = dict([(str, 's'),
                   (int, 'd'), \
                   (float, ''), #'.1f'\
		   (np.float64, '') #'.1f'
                  ]
                 )
    if decimals is not None:
        assert type(decimals) is int
        dident[float] = '.{}f'.format(decimals)
        dident[np.float64] = '.{}f'.format(decimals)
                 
    if not hasattr(dtypes, '__iter__'):
        dtypes = [dtypes,] * num_vals
    elif type(dtypes) is str:
        dtypes = [dtypes,] * num_vals
    elif len(dtypes) < num_vals:
        dtypes = [dtypes[0],] * num_vals
         
    for dt in dtypes:
        assert dt in dident.keys(), dt
    
    # construct actual output
    out = ""
    for i in range(num_vals):
        out += "{" + str(i) + ":" + dident[dtypes[i]] + "}"
        out += sep
    
    # remove additional separator from output
    return out[:-len(sep)]

def find_decimals(value, maxlen=10):
	"""
	Find the decimal representation of `value`.

	`maxlen` is the maximal number of digits.
	"""
	e = np.floor(np.log10(value)) # exponent
	b = [] # list of decimals
	new_rep = 0
	vi = value
	i = 0
	while abs(new_rep - value) > 1e-10:
		bi = np.floor(vi / 10**(e-i))
		b.append(int(bi))
		vi = vi - b[-1] * 10**(e-i)
		new_rep = sum([bv * 10**(e-bj) for bj, bv in enumerate(b)])
		#print new_rep
		i += 1
		if i >= 100:
			break
	
	if new_rep - value > 0:
		b[-1] = b[-1] - 1 if b[-1] > 0 else 0
	elif new_rep - value < 0:
		i = 0
		for bv in b[::-1]:
			if bv != 9:
				break
			i += 1
		b[-i-1] = b[-i-1] + 1
		b = b[:-i]

	return b if len(b) <= maxlen else b[:maxlen]

def find_decimals1(num):
	
	err = lambda x: x-np.round(x)
	e = 0
	v = num
	while err(v) != 0:
		e += 1
		#print(e)
		#print(num)
		v = num * 10**e
		#print(v)
		#print(err(v))
	
	if err(v) < 0:
		e += 1
	
	return e


def find_max_num_decimals(values):
	"""
	Find the maximum number of decimals for an interable of values
	or a single value. The decimal point is included in the return value.
	"""

	maxnum = 0
	if isiterable(values):
		for v in values:
			b = find_decimals(v)
			maxnum = max([maxnum, len(b)+1])
	else:
		b = find_decimals(values)
		maxnum = maxnum
	
	return maxnum

def str_to_bool(string):
	"""
	Convert string to bool.
	Not case sensitive.
	"""
	if string.lower() in "true":
		return True
	elif string.lower() == "false":
		return False
	else:
		raise Exception("Cannot convert '{}' to bool.".format(string))