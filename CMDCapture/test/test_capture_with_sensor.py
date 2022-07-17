import os
import shutil
import unittest
import capture
import argparse

"""
Unit tests for Capture - This requires a sensor plugged in
"""


class TestCaptureSensor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCaptureSensor, cls).setUpClass()

    # shutil.rmtree('results', ignore_errors=True)
    # os.mkdir('results')

    def setup_args(self):
        shutil.rmtree('results', ignore_errors=True)
        args = argparse.Namespace()
        args.filename = ''  # os.path.join("results", "test")
        args.port = None
        args.start = 5
        args.units = 'm'
        args.distance_range = [0, 10]
        args.angle_range = [-55, 55]
        args.fps = 2
        return args

    def test_xyz(self):
        args = self.setup_args()
        args.format = 'xyz'
        capture.main(args)

    def test_pcd(self):
        args = self.setup_args()
        args.format = 'pcd'
        capture.main(args)

    def test_ply(self):
        args = self.setup_args()
        args.format = 'ply'
        capture.main(args)

    def test_las(self):
        args = self.setup_args()
        args.format = 'las'
        capture.main(args)
