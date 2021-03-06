# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Unit tests for tensor formatter."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin

from tensorflow.python.debug.cli import tensor_format
from tensorflow.python.framework import test_util
from tensorflow.python.platform import googletest


class RichTextLinesTest(test_util.TensorFlowTestCase):

  def setUp(self):
    np.set_printoptions(
        precision=8, threshold=1000, edgeitems=3, linewidth=75)

  def _checkTensorMetadata(self, tensor, annotations):
    self.assertEqual(
        {"dtype": tensor.dtype, "shape": tensor.shape},
        annotations["tensor_metadata"])

  def _checkBeginIndices(self, expected_indices, annot):
    self.assertEqual({tensor_format.BEGIN_INDICES_KEY: expected_indices},
                     annot)

  def _checkOmittedIndices(self, expected_indices, annot):
    self.assertEqual({tensor_format.OMITTED_INDICES_KEY: expected_indices},
                     annot)

  def testFormatZeroDimensionTensor(self):
    a = np.array(42.0, dtype=np.float32)

    out = tensor_format.format_tensor(a, "a")

    self.assertEqual(["Tensor \"a\":", "", "array(42.0, dtype=float32)"],
                     out.lines)
    self._checkTensorMetadata(a, out.annotations)

  def testFormatTensor1DNoEllipsis(self):
    a = np.zeros(20)

    out = tensor_format.format_tensor(
        a, "a", np_printoptions={"linewidth": 40})

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([ 0.,  0.,  0.,  0.,  0.,  0.,",
        "        0.,  0.,  0.,  0.,  0.,  0.,",
        "        0.,  0.,  0.,  0.,  0.,  0.,",
        "        0.,  0.])",
    ], out.lines)

    self._checkTensorMetadata(a, out.annotations)

    # Check annotations for beginning indices of the lines.
    self._checkBeginIndices([0], out.annotations[2])
    self._checkBeginIndices([6], out.annotations[3])
    self._checkBeginIndices([12], out.annotations[4])
    self._checkBeginIndices([18], out.annotations[5])

  def testFormatTensor2DNoEllipsisNoRowBreak(self):
    a = np.linspace(0.0, 1.0 - 1.0 / 16.0, 16).reshape([4, 4])

    out = tensor_format.format_tensor(a, "a")

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([[ 0.    ,  0.0625,  0.125 ,  0.1875],",
        "       [ 0.25  ,  0.3125,  0.375 ,  0.4375],",
        "       [ 0.5   ,  0.5625,  0.625 ,  0.6875],",
        "       [ 0.75  ,  0.8125,  0.875 ,  0.9375]])",
    ], out.lines)

    self._checkTensorMetadata(a, out.annotations)

    # Check annotations for the beginning indices of the lines.
    for i in xrange(2, 6):
      self._checkBeginIndices([i  - 2, 0], out.annotations[i])

  def testFormatTensorSuppressingTensorName(self):
    a = np.linspace(0.0, 1.0 - 1.0 / 16.0, 16).reshape([4, 4])

    out = tensor_format.format_tensor(a, None)

    self.assertEqual([
        "array([[ 0.    ,  0.0625,  0.125 ,  0.1875],",
        "       [ 0.25  ,  0.3125,  0.375 ,  0.4375],",
        "       [ 0.5   ,  0.5625,  0.625 ,  0.6875],",
        "       [ 0.75  ,  0.8125,  0.875 ,  0.9375]])",
    ], out.lines)

    self._checkTensorMetadata(a, out.annotations)

    # Check annotations for the beginning indices of the lines.
    for i in xrange(4):
      self._checkBeginIndices([i, 0], out.annotations[i])

  def testFormatTensorWithMetadata(self):
    a = np.linspace(0.0, 1.0 - 1.0 / 16.0, 16).reshape([4, 4])

    out = tensor_format.format_tensor(a, "a", include_metadata=True)

    self.assertEqual([
        "Tensor \"a\":",
        "  dtype: float64",
        "  shape: (4, 4)",
        "",
        "array([[ 0.    ,  0.0625,  0.125 ,  0.1875],",
        "       [ 0.25  ,  0.3125,  0.375 ,  0.4375],",
        "       [ 0.5   ,  0.5625,  0.625 ,  0.6875],",
        "       [ 0.75  ,  0.8125,  0.875 ,  0.9375]])",
    ], out.lines)

    self._checkTensorMetadata(a, out.annotations)

    # Check annotations for the beginning indices of the lines.
    for i in xrange(4, 7):
      self._checkBeginIndices([i  - 4, 0], out.annotations[i])

  def testFormatTensor2DNoEllipsisWithRowBreak(self):
    a = np.linspace(0.0, 1.0 - 1.0 / 40.0, 40).reshape([2, 20])

    out = tensor_format.format_tensor(
        a, "a", np_printoptions={"linewidth": 50})

    self.assertEqual(
        {"dtype": a.dtype, "shape": a.shape},
        out.annotations["tensor_metadata"])

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([[ 0.   ,  0.025,  0.05 ,  0.075,  0.1  ,",
        "         0.125,  0.15 ,  0.175,  0.2  ,  0.225,",
        "         0.25 ,  0.275,  0.3  ,  0.325,  0.35 ,",
        "         0.375,  0.4  ,  0.425,  0.45 ,  0.475],",
        "       [ 0.5  ,  0.525,  0.55 ,  0.575,  0.6  ,",
        "         0.625,  0.65 ,  0.675,  0.7  ,  0.725,",
        "         0.75 ,  0.775,  0.8  ,  0.825,  0.85 ,",
        "         0.875,  0.9  ,  0.925,  0.95 ,  0.975]])",
    ], out.lines)

    self._checkTensorMetadata(a, out.annotations)

    # Check annotations for the beginning indices of the lines.
    self._checkBeginIndices([0, 0], out.annotations[2])
    self._checkBeginIndices([0, 5], out.annotations[3])
    self._checkBeginIndices([0, 10], out.annotations[4])
    self._checkBeginIndices([0, 15], out.annotations[5])
    self._checkBeginIndices([1, 0], out.annotations[6])
    self._checkBeginIndices([1, 5], out.annotations[7])
    self._checkBeginIndices([1, 10], out.annotations[8])
    self._checkBeginIndices([1, 15], out.annotations[9])

  def testFormatTensor3DNoEllipsis(self):  # TODO(cais): Test name.
    a = np.linspace(0.0, 1.0 - 1.0 / 24.0, 24).reshape([2, 3, 4])

    out = tensor_format.format_tensor(a, "a")

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([[[ 0.        ,  0.04166667,  0.08333333,  0.125     ],",
        "        [ 0.16666667,  0.20833333,  0.25      ,  0.29166667],",
        "        [ 0.33333333,  0.375     ,  0.41666667,  0.45833333]],",
        "",
        "       [[ 0.5       ,  0.54166667,  0.58333333,  0.625     ],",
        "        [ 0.66666667,  0.70833333,  0.75      ,  0.79166667],",
        "        [ 0.83333333,  0.875     ,  0.91666667,  0.95833333]]])",
    ], out.lines)

    self._checkTensorMetadata(a, out.annotations)

    # Check annotations for beginning indices of the lines.
    self._checkBeginIndices([0, 0, 0], out.annotations[2])
    self._checkBeginIndices([0, 1, 0], out.annotations[3])
    self._checkBeginIndices([0, 2, 0], out.annotations[4])
    self.assertNotIn(5, out.annotations)
    self._checkBeginIndices([1, 0, 0], out.annotations[6])
    self._checkBeginIndices([1, 1, 0], out.annotations[7])
    self._checkBeginIndices([1, 2, 0], out.annotations[8])

  def testFormatTensorWithEllipses(self):
    a = np.zeros([11, 11, 11])

    out = tensor_format.format_tensor(
        a, "a", False, np_printoptions={"threshold": 100, "edgeitems": 2})

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([[[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]],",
        "",
        "       [[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]],",
        "",
        "       ..., ",
        "       [[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]],",
        "",
        "       [[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]]])",
    ], out.lines)

    self._checkTensorMetadata(a, out.annotations)

    # Check annotations for beginning indices of the lines.
    for i in xrange(2):
      self._checkBeginIndices([i, 0, 0], out.annotations[i * 6 + 2])
      self._checkBeginIndices([i, 1, 0], out.annotations[i * 6 + 3])
      self._checkOmittedIndices([i, 2, 0], out.annotations[i * 6 + 4])
      self._checkBeginIndices([i, 9, 0], out.annotations[i * 6 + 5])
      self._checkBeginIndices([i, 10, 0], out.annotations[i * 6 + 6])
      self.assertNotIn(i * 6 + 7, out.annotations)

    p = 15
    for i in xrange(2):
      self._checkBeginIndices([9 + i, 0, 0], out.annotations[p + i * 6])
      self._checkBeginIndices([9 + i, 1, 0], out.annotations[p + i * 6 + 1])
      self._checkOmittedIndices(
          [9 + i, 2, 0], out.annotations[p + i * 6 + 2])
      self._checkBeginIndices([9 + i, 9, 0], out.annotations[p + i * 6 + 3])
      self._checkBeginIndices([9 + i, 10, 0], out.annotations[p + i * 6 + 4])

      if i < 1:
        self.assertNotIn(p + i * 6 + 5, out.annotations)

  def testFormatNone(self):
    out = tensor_format.format_tensor(None, "a")

    self.assertEqual(
        ["Tensor \"a\":", "", "None"], out.lines)

  def testLocateTensorElement1DNoEllipsis(self):
    a = np.zeros(20)

    out = tensor_format.format_tensor(
        a, "a", np_printoptions={"linewidth": 40})

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([ 0.,  0.,  0.,  0.,  0.,  0.,",
        "        0.,  0.,  0.,  0.,  0.,  0.,",
        "        0.,  0.,  0.,  0.,  0.,  0.,",
        "        0.,  0.])",
    ], out.lines)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0])
    self.assertFalse(is_omitted)
    self.assertEqual(2, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [5])
    self.assertFalse(is_omitted)
    self.assertEqual(2, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [6])
    self.assertFalse(is_omitted)
    self.assertEqual(3, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [11])
    self.assertFalse(is_omitted)
    self.assertEqual(3, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [12])
    self.assertFalse(is_omitted)
    self.assertEqual(4, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [18])
    self.assertFalse(is_omitted)
    self.assertEqual(5, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [19])
    self.assertFalse(is_omitted)
    self.assertEqual(5, row)

    with self.assertRaisesRegexp(
        ValueError, "Indices exceed tensor dimensions"):
      tensor_format.locate_tensor_element(out, [20])

    with self.assertRaisesRegexp(
        ValueError, "Indices contain negative"):
      tensor_format.locate_tensor_element(out, [-1])

    with self.assertRaisesRegexp(
        ValueError, "Dimensions mismatch"):
      tensor_format.locate_tensor_element(out, [0, 0])

  def testLocateTensorElement2DNoEllipsis(self):
    a = np.linspace(0.0, 1.0 - 1.0 / 16.0, 16).reshape([4, 4])

    out = tensor_format.format_tensor(a, "a")

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([[ 0.    ,  0.0625,  0.125 ,  0.1875],",
        "       [ 0.25  ,  0.3125,  0.375 ,  0.4375],",
        "       [ 0.5   ,  0.5625,  0.625 ,  0.6875],",
        "       [ 0.75  ,  0.8125,  0.875 ,  0.9375]])",
    ], out.lines)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 0])
    self.assertFalse(is_omitted)
    self.assertEqual(2, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 3])
    self.assertFalse(is_omitted)
    self.assertEqual(2, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [1, 0])
    self.assertFalse(is_omitted)
    self.assertEqual(3, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [1, 3])
    self.assertFalse(is_omitted)
    self.assertEqual(3, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [3, 3])
    self.assertFalse(is_omitted)
    self.assertEqual(5, row)

    with self.assertRaisesRegexp(
        ValueError, "Indices exceed tensor dimensions"):
      tensor_format.locate_tensor_element(out, [1, 4])

    with self.assertRaisesRegexp(
        ValueError, "Indices contain negative"):
      tensor_format.locate_tensor_element(out, [-1, 2])

    with self.assertRaisesRegexp(
        ValueError, "Dimensions mismatch"):
      tensor_format.locate_tensor_element(out, [0])

  def testLocateTensorElement3DWithEllipses(self):
    a = np.zeros([11, 11, 11])

    out = tensor_format.format_tensor(
        a, "a", False, np_printoptions={"threshold": 100, "edgeitems": 2})

    self.assertEqual([
        "Tensor \"a\":",
        "",
        "array([[[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]],",
        "",
        "       [[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]],",
        "",
        "       ..., ",
        "       [[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]],",
        "",
        "       [[ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        ..., ",
        "        [ 0.,  0., ...,  0.,  0.],",
        "        [ 0.,  0., ...,  0.,  0.]]])",
    ], out.lines)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 0, 0])
    self.assertFalse(is_omitted)
    self.assertEqual(2, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 0, 10])
    self.assertFalse(is_omitted)
    self.assertEqual(2, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 1, 0])
    self.assertFalse(is_omitted)
    self.assertEqual(3, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 2, 0])
    self.assertTrue(is_omitted)  # In omitted line.
    self.assertEqual(4, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 2, 10])
    self.assertTrue(is_omitted)  # In omitted line.
    self.assertEqual(4, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 8, 10])
    self.assertTrue(is_omitted)  # In omitted line.
    self.assertEqual(4, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [0, 10, 1])
    self.assertFalse(is_omitted)
    self.assertEqual(6, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [5, 1, 1])
    self.assertTrue(is_omitted)  # In omitted line.
    self.assertEqual(14, row)

    is_omitted, row = tensor_format.locate_tensor_element(out, [10, 10, 10])
    self.assertFalse(is_omitted)
    self.assertEqual(25, row)

    with self.assertRaisesRegexp(
        ValueError, "Indices exceed tensor dimensions"):
      tensor_format.locate_tensor_element(out, [11, 5, 5])

    with self.assertRaisesRegexp(
        ValueError, "Indices contain negative"):
      tensor_format.locate_tensor_element(out, [-1, 5, 5])

    with self.assertRaisesRegexp(
        ValueError, "Dimensions mismatch"):
      tensor_format.locate_tensor_element(out, [5, 5])

  def testLocateTensorElementAnnotationsUnavailable(self):
    out = tensor_format.format_tensor(None, "a")

    self.assertEqual(
        ["Tensor \"a\":", "", "None"], out.lines)

    with self.assertRaisesRegexp(
        AttributeError, "tensor_metadata is not available in annotations"):
      tensor_format.locate_tensor_element(out, [0])


if __name__ == "__main__":
  googletest.main()
