#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Script to run all unit tests in this package."""


import document_test
import model_test
import module_test_runner
import ops_test
import robot_abstract_test
import util_test


def RunUnitTests():
  """Runs all registered unit tests."""
  test_runner = module_test_runner.ModuleTestRunner()
  test_runner.modules = [
      document_test,
      model_test,
      ops_test,
      robot_abstract_test,
      util_test,
  ]
  test_runner.RunAllTests()


if __name__ == "__main__":
  RunUnitTests()
