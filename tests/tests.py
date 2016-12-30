from testenv import TestCase

import ../core/scancel as scancel

class ScancelTests(TestCase):
    """
    Tests for scancel.
    """

    def test_process_input_none():
        assert(scancel.process_input([]) == [None, None])
    
    def test_process_input_l():
        assert(scancel.process_input(["-l", 5]) == ["last", 5])

    def test_process_input_f():
        assert(scancel.process_input(["-f", 5]) == ["first", 5])
    
    def test_process_input_ind():
        assert(scancel.process_input([5]) == ["ind", 5])