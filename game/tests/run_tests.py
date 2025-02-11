import unittest
from django.test.runner import DiscoverRunner

def run_tests():
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['game'])
    if failures:
        print(f"Tests failed: {failures} test(s) failed")
    else:
        print("All tests passed!")

if __name__ == '__main__':
    run_tests()