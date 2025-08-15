'''
This is the object that is used in run_test_cases.py, read the run method docstring for an explanation
'''

class Answer:
    def __init__(self):
        pass

    def run(self, method: str, *args, **kwargs):
        '''
        the run method is what is called in the run_test_cases.py file
        it receives the method name, a list of args, and a dict of kwargs. 
        make sure to implement the appropriate methods in Answer.
        
        you may create other classes, but you still need a wrapper for the methods 
        in Answer that calls the method of the custom class, and make sure 
        to instantiate the custom class if you choose to do this
        '''
        return getattr(self, method)(*args, **kwargs)

