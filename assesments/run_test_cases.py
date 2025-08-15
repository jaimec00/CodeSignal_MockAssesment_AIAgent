import argparse
import unittest
import json
import importlib.util
import sys
from pathlib import Path

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

                    output = answer.run(operation["method"], *operation.get("args", []), **operation.get("kwargs", {}))
                    expected = operation["output"]

                    incorrect_str = f"\n\nincorrect output:\n\tlevel: {level}\n\ttestcase: {testcase_idx}\n\toperation: {operation_idx}"\
                                    f"\n\tmethod: {operation['method']}\n\targs: {operation.get('args', [])}\n\tkwargs: {operation.get('kwargs', {})}"\
                                    f"\n\texpected {expected}\n\tgot {output}\n"

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