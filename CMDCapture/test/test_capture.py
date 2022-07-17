import unittest
import capture
import numpy as np

"""
Unit tests for Capture
"""


class TestCapture(unittest.TestCase):

    def test_xyz(self):
        data = np.asarray([[1, 2, 3, 10, 20], [3, 4, 5, 11, 21], [6, 7, 8, 12, 22]])
        formatted = capture.xyz(data)
        expected = 'X Y Z Intensity Velocity\n' \
                   '1 2 3 10 20\n' \
                   '3 4 5 11 21\n' \
                   '6 7 8 12 22\n'
        self.assertEqual(expected, formatted)

    def test_pcd(self):
        data = np.asarray([[1, 2, 3, 10, 20], [3, 4, 5, 11, 21], [6, 7, 8, 12, 22]])
        formatted = capture.pcd(data)
        expected = "# .PCD v.7 - Point Cloud Data file format\n" \
                   "VERSION .7\n" \
                   "FIELDS x y z intensity velocity\n" \
                   "SIZE 4 4 4 4 4\n" \
                   "TYPE F F F F F\n" \
                   "COUNT 1 1 1 1 1\n" \
                   "WIDTH 1\n" \
                   "HEIGHT 1\n" \
                   "VIEWPOINT 0 0 0 1 0 0 0\n" \
                   "POINTS 3\n" \
                   "DATA ascii\n" \
                   '1 2 3 10 20\n' \
                   '3 4 5 11 21\n' \
                   '6 7 8 12 22\n'
        self.assertEqual(expected, formatted)

    def test_ply(self):
        data = np.asarray([[1, 2, 3, 10, 20], [3, 4, 5, 11, 21], [6, 7, 8, 12, 22]])
        formatted = capture.ply(data)
        expected = "ply\n" \
                   "format ascii 1.0\n" \
                   "element vertex 3\n" \
                   "property float x\n" \
                   "property float y\n" \
                   "property float z\n" \
                   "property float intensity\n" \
                   "property float velocity\n" \
                   "end_header\n" \
                   '1 2 3 10 20\n' \
                   '3 4 5 11 21\n' \
                   '6 7 8 12 22\n'
        self.assertEqual(expected, formatted)

    def test_las(self):
        data = np.asarray([[1, 2, 3, 10, 20], [3, 4, 5, 11, 21], [6, 7, 8, 12, 22]])
        x, y, z, intensities, velocities = capture._prepare_las(data)
        self.assertListEqual([1, 3, 6], x.tolist())
        self.assertListEqual([2, 4, 7], y.tolist())
        self.assertListEqual([3, 5, 8], z.tolist())
        self.assertListEqual([10, 11, 12], intensities.tolist())
        self.assertListEqual([20, 21, 22], velocities.tolist())

    def test_build_filename(self):
        unchanged_extension = capture.build_filename('test.xyz', 'xyz', 1)
        self.assertEqual('test_001.xyz', unchanged_extension)

        updated_extension = capture.build_filename('test', 'xyz', 1)
        self.assertEqual('test_001.xyz', updated_extension)

        file_count = capture.build_filename('test.xyz', 'xyz', 5)
        self.assertEqual('test_005.xyz', file_count)
