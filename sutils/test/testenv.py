class TestCase(object):
    """
    Base class for tests.
    """

    @classmethod
    def run(cls):
        """
        Runs all tests (methods which begin with 'test').
        """
        #print(cls)
        max_len = max([len(a) for a in cls.__dict__])
        for key in cls.__dict__:
            if key.startswith("test"):
                fill = max_len - len(key)
                sys.stdout.write("Testing {} ...{} ".format(key, '.'*fill))
                try:
                    cls.__dict__[key]()
                except:
                    raise
                else:
                    print("Test passed!")
        print("All tests passed!")