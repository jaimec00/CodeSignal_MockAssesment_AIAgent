import argparse
import unittest
import json
import importlib.util
import sys
from pathlib import Path

exceptions = {
    "ArithmeticError": ArithmeticError,
    "FloatingPointError": FloatingPointError,
    "OverflowError": OverflowError,
    "ZeroDivisionError": ZeroDivisionError,
    "AssertionError": AssertionError,
    "AttributeError": AttributeError,
    "BufferError": BufferError,
    "EOFError": EOFError,
    "ImportError": ImportError,
    "ModuleNotFoundError": ModuleNotFoundError,
    "LookupError": LookupError,
    "IndexError": IndexError,
    "KeyError": KeyError,
    "MemoryError": MemoryError,
    "NameError": NameError,
    "UnboundLocalError": UnboundLocalError,
    "OSError": OSError,
    "BlockingIOError": BlockingIOError,
    "ChildProcessError": ChildProcessError,
    "ConnectionError": ConnectionError,
    "BrokenPipeError": BrokenPipeError,
    "ConnectionAbortedError": ConnectionAbortedError,
    "ConnectionRefusedError": ConnectionRefusedError,
    "ConnectionResetError": ConnectionResetError,
    "FileExistsError": FileExistsError,
    "FileNotFoundError": FileNotFoundError,
    "InterruptedError": InterruptedError,
    "IsADirectoryError": IsADirectoryError,
    "NotADirectoryError": NotADirectoryError,
    "PermissionError": PermissionError,
    "ProcessLookupError": ProcessLookupError,
    "TimeoutError": TimeoutError,
    "ReferenceError": ReferenceError,
    "RuntimeError": RuntimeError,
    "NotImplementedError": NotImplementedError,
    "RecursionError": RecursionError,
    "StopIteration": StopIteration,
    "StopAsyncIteration": StopAsyncIteration,
    "SyntaxError": SyntaxError,
    "IndentationError": IndentationError,
    "TabError": TabError,
    "SystemError": SystemError,
    "TypeError": TypeError,
    "ValueError": ValueError,
    "UnicodeError": UnicodeError,
    "UnicodeDecodeError": UnicodeDecodeError,
    "UnicodeEncodeError": UnicodeEncodeError,
    "UnicodeTranslateError": UnicodeTranslateError
}

def main(args):

    # load the testcases
    testcases = {}
    for testcase_idx in range(1,5):
        with open(args.assesment_dir / Path(f"testcases/level{testcase_idx}.json"), "r", encoding="utf-8") as f:
            testcases[str(testcase_idx)] = json.load(f)
    
    # load the answer dynamically
    answer_path = args.assesment_dir / Path("answer.py")
    spec = importlib.util.spec_from_file_location("module", answer_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module"] = module
    spec.loader.exec_module(module)

    # define the unit tests
    class Test(unittest.TestCase):

        def check_testcases(self, level):

            for testcase_idx, testcase in testcases.get(str(level), {}).items():
                
                # reset the implementation for every testcase
                answer = module.Answer()

                for operation_idx, operation in enumerate(testcase):

                    expected = operation["output"]
                    method, args, kwargs = operation["method"], operation["args"], operation["kwargs"]
                    incorrect_str = (f"\n\nincorrect output:\n\tlevel: {level}\n\ttestcase: {testcase_idx}\n\toperation: {operation_idx}"
                                    f"\n\tmethod: {method}\n\targs: {args}\n\tkwargs: {kwargs}"
                                    f"\n\texpected: {expected}")

                    try:
                        output = answer.run(method, *args, **kwargs)
                    except Exception as e: # if it raises an exception, check if it is the expected one
                        if isinstance(expected, str) and expected in exceptions:
                            expected = exceptions[expected]
                            output = type(e)
                        else:
                            print(incorrect_str + f"\n\tgot: {type(e)}\n")
                            raise e

                    incorrect_str += f"\n\tgot: {output}\n"
                    self.assertEqual(output, expected, incorrect_str)
            
        def test_level1(self):
            self.check_testcases(1)

        def test_level2(self):
            self.check_testcases(2)

        def test_level3(self):
            self.check_testcases(3)

        def test_level4(self):
            self.check_testcases(4)

    # define which tests to run
    loader = unittest.TestLoader()
    if args.level == 0: # run all
        suite = loader.loadTestsFromTestCase(Test)
    else: # run only one of them
        method_name = f"test_level{args.level}"
        if not hasattr(Test, method_name):
            raise SystemExit(f"No such test method: {method_name}. Use --level 1..4 or 0 for all.")
        suite = unittest.TestSuite()
        suite.addTest(Test(method_name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--assesment_dir",  type=Path, default="base", 
                                            help="path to the directory where the assesment is taking place")
    parser.add_argument("--level",          type=int, default=0, 
                                            help="levels to test (1-4). 0 means run all") 

    args = parser.parse_args()

    main(args)