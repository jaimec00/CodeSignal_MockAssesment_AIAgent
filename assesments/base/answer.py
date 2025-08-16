'''
This is the object that is used in run_test_cases.py
the run method is what is called in the run_test_cases.py file
it receives the method name, a list of args, and a dict of kwargs. 
make sure to implement the appropriate methods in Answer.

you may create other classes, but you still need a wrapper for the methods 
in Answer that calls the method of the custom class, and make sure 
to instantiate the custom class if you choose to do this
'''

class Answer:
    def __init__(self):
        pass # edit as needed

    def run(self, method: str, *args, **kwargs): # do not edit this method
        return getattr(self, method)(*args, **kwargs)

    # Your implemented methods go here (feel free to edit/delete this)
    def EXAMPLE_METHOD(self, arg1: int, arg2: str, kwarg1: str=""):
        '''
        description:    this is an example description of the method to implement
        params:         arg1 (int):     an example integer
                        arg2 (str):     an example string
                        kwarg (str):    an example kwarg string
        returns:        None | str:     an example return value
        notes:                          any special cases the user should know about
        '''
        pass

# also feel free to create custom classes, 
# just make sure they are instantiated by Answer
class ExampleClass: # feel free to edit/delete this
    def __init__(self):
        pass

