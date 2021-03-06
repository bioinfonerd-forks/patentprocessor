#!/usr/bin/env python

import unittest
import os
import logging
import sys
import subprocess

# Setup test files and logs
dir = os.path.dirname(__file__)
testdir = os.path.join(dir, '/test/fixtures/xml')
log_file = os.path.join(dir, './fixtures/unittest/unit-test.log')

# Logging setup
logging.basicConfig(filename=log_file, level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)


class TestPatentConfig(unittest.TestCase):
    # Make sure that if os.environ['PATENTROOT'] is set, then we parse it correctly
    # if it is nonexistant/incorrect, then recover
    # if it is not set, then we default to /data/patentdata/patents

    def setUp(self):
        # make sure we can call parse.py using the os module
        # for the purpose of testing command line arguments
        self.null_out = open('/dev/null','wb')
        current_directory = os.getcwd()
        if not current_directory.endswith('test'):
            logging.error('Please run from the patentprocessor/test directory')
        # test existence of PATENTROOT; set it to reasonable default if nonexistant
        if not os.environ.has_key('PATENTROOT'):
            logging.error('Cannot find PATENTROOT environment variable. Setting ' +
                'PATENTROOT to the patentprocessor directory for the scope of this test. ' +
                'Use `export PATENTROOT=/path/to/directory` to change')
            os.environ['PATENTROOT'] = os.getcwd()
        self.assertTrue(os.access(os.environ['PATENTROOT'], os.F_OK), msg='PATENTROOT directory does not exist')
        self.assertTrue(os.access(os.environ['PATENTROOT'], os.R_OK), msg='PATENTROOT directory is not readable')
        self.assertTrue(os.environ.has_key('PATENTROOT'))
        os.chdir('..')

    def test_argparse_patentroot(self):
        # test that argparse is setting the variables correctly for patentroot
        exit_status = subprocess.call('python parse.py -xasdf --patentroot %s' % \
                (os.getcwd() + testdir), \
                stdout=self.null_out, shell=True)
        # valid directory, but no xml files
        self.assertTrue(exit_status == 1)

    def test_argparse_invalid_directory(self):
        if not os.path.exists('/tmp/asdf'):
            os.mkdir('/tmp/asdf')
        exit_status = subprocess.call('python parse.py --patentroot /tmp/asdf', \
                stdout=self.null_out, shell=True)
        # specify invalid directory, should not have any files
        os.rmdir('/tmp/asdf')
        self.assertTrue(exit_status == 1)

    def test_argparse_valid_directory(self):
        # test a working, valid directory without xml files
        exit_status = subprocess.call('python parse.py --patentroot %s' % \
                (os.environ['PATENTROOT']), stdout=self.null_out, shell=True)
        self.assertTrue(exit_status == 1)

    def test_argparse_regex(self):
        # test that argparse is setting the regular expression correctly
        # test valid regex on fixtures/xml folder
        exit_status = subprocess.call("python parse.py \
                --patentroot %s --xmlregex 'ipg120327.one.xml'" % \
                (os.getcwd() + testdir), \
                stdout=self.null_out, shell=True)
        self.assertTrue(exit_status == 0,os.getcwd()+testdir)

    def test_argparse_directory(self):
        # test that argparse is setting the variables correctly for directories
        # parse.py should not find any .xml files
        base = '/'.join(testdir.split('/')[:-1])
        top = testdir.split('/')[-1]
        exit_status = subprocess.call('python parse.py --patentroot %s' % \
                (os.getcwd() + base), stdout=self.null_out, shell=True)
        self.assertTrue(exit_status == 1)

    def test_argparse_directory_withxml(self):
        # parse.py should concatentate the correct directory and find xml files
        base = '/'.join(testdir.split('/')[:-1])
        top = testdir.split('/')[-1]
        exit_status = subprocess.call("python parse.py --patentroot %s \
                --directory %s --xmlregex 'ipg120327.one.xml'" % \
                (os.getcwd() + base, top), stdout=self.null_out, shell=True)
        self.assertTrue(exit_status == 0)

        # TODO: make test for iterating through multiple directories

    def test_gets_environment_var(self):
        # sanity check for existing valid path
        logging.info("Testing getting valid env var PATENTROOT")
        self.assertTrue(os.environ.has_key('PATENTROOT'))

    def tearDown(self):
        os.chdir('test')

if __name__ == '__main__':

    open(log_file, 'w')
    unittest.main()
