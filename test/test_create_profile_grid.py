# coding=utf-8
"""Tests for createProfileGrid (profile grid creation, including axes with no profile data).

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import unittest

from utilities import get_qgis_app

# Only import after QGIS app is initialized
QGIS_APP = get_qgis_app()


@unittest.skipIf(QGIS_APP[0] is None, "QGIS not available")
class TestCreateProfileGrid(unittest.TestCase):
    """Test createProfileGrid does not raise when some axes have no profile data."""

    def test_create_profile_grid_with_axes_without_profile_data_no_overflow(self):
        """When profile features exist only for a subset of axes, createProfileGrid
        should not raise OverflowError (invalid extents are skipped)."""
        from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField
        from PyQt5.QtCore import QVariant
        from qgistrati.qgistrati import createProfileGrid

        # Axis layer: two line features (axis ids 1 and 2)
        axis_layer = QgsVectorLayer(
            "LineString?crs=EPSG:32630&field=axis_id:integer",
            "axes",
            "memory",
        )
        axis_layer.dataProvider().addAttributes([QgsField("axis_id", QVariant.Int)])
        axis_layer.updateFields()
        for axis_id, coords in [(1, [(0, 0), (10, 0)]), (2, [(0, 5), (10, 5)])]:
            f = QgsFeature(axis_layer.fields())
            f.setAttribute("axis_id", axis_id)
            f.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(x, y) for x, y in coords]))
            axis_layer.dataProvider().addFeature(f)

        # Profile layer: one point on axis 1 only (axis 2 will have no profile data → inf extent)
        profile_layer = QgsVectorLayer(
            "Point?crs=EPSG:32630&field=axis_id:integer",
            "profile_points",
            "memory",
        )
        profile_layer.dataProvider().addAttributes([QgsField("axis_id", QVariant.Int)])
        profile_layer.updateFields()
        feat = QgsFeature(profile_layer.fields())
        feat.setAttribute("axis_id", 1)
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(5, 2)))
        profile_layer.dataProvider().addFeature(feat)

        # Should not raise OverflowError (previously: math.floor(inf) on axis 2)
        result = createProfileGrid(
            profile_layer,
            axis_layer,
            vertical_exaggeration=1.0,
            interval=0.5,
            extremities=False,
            progress_bar=None,
            crs=32630,
        )
        self.assertIsNotNone(result, "createProfileGrid should return a grid layer")
        self.assertTrue(hasattr(result, "featureCount"), "result should be a vector layer")
        # Grid is built only for axes with profile data (axis 1); axis 2 is skipped
        self.assertGreater(result.featureCount(), 0, "grid should have lines for the axis that has profile data")


if __name__ == "__main__":
    unittest.main()
