class Logger(object):
    def __init__(self):
        raise Exception("Attempt to instantiate a static class")
    
    @staticmethod
    def log(*args):
        print(f"\x1b[47m\x1b[30mLOG\x1b[0m {' '.join(args)}\x1b[0m")
    
    @staticmethod
    def error(*args):
        print(f"\x1b[41mERROR\x1b[0m \x1b[31m{' '.join([str(x) for x in args])}\x1b[0m")
    
    @staticmethod
    def warn(*args):
        print(f"\x1b[43m\x1b[30mWARNING\x1b[0m \x1b[33m{' '.join(args)}\x1b[0m")
    
    @staticmethod
    def debug(*args):
        print(f"\x1b[47m\x1b[30mDEBUG\x1b[0m \x1b[34m{' '.join(args)}\x1b[0m")

