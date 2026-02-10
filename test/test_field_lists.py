# coding=utf-8
"""Tests for field list helpers (listFieldNames, listNumericFields, NUMERIC_FIELD_TYPE_NAMES).

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import unittest

from utilities import get_qgis_app

# Only import plugin modules after QGIS app is initialized
QGIS_APP = get_qgis_app()


@unittest.skipIf(QGIS_APP[0] is None, "QGIS not available")
class TestFieldLists(unittest.TestCase):
    """Test listFieldNames, listNumericFields and NUMERIC_FIELD_TYPE_NAMES."""

    def test_list_field_names_empty_list_returns_empty_list(self):
        """listFieldNames([]) returns [] and does not treat empty as invalid."""
        from qgistrati.qgistrati import listFieldNames
        result = listFieldNames([])
        self.assertIsNotNone(result)
        self.assertEqual(result, [])

    def test_numeric_field_type_names_include_postgres_types(self):
        """NUMERIC_FIELD_TYPE_NAMES includes types used by PostgreSQL and temporary layers."""
        from qgistrati.qgistrati import NUMERIC_FIELD_TYPE_NAMES
        expected = {'numeric', 'decimal', 'float4', 'float8', 'double precision'}
        for name in expected:
            self.assertIn(
                name,
                NUMERIC_FIELD_TYPE_NAMES,
                "NUMERIC_FIELD_TYPE_NAMES should include %r for PostgreSQL/temporary layers" % name,
            )

    def test_list_field_names_returns_sorted_names(self):
        """listFieldNames with QgsField list returns sorted field names."""
        from qgis.core import QgsField
        from qgistrati.qgistrati import listFieldNames
        # Build list of QgsField with typeName so they are valid
        fields = [
            QgsField("altitude", 6),   # QVariant.Double
            QgsField("depth", 6),
        ]
        result = listFieldNames(fields)
        self.assertEqual(result, ["altitude", "depth"])

    def test_list_field_names_non_list_returns_none(self):
        """listFieldNames with non-list returns None."""
        from qgistrati.qgistrati import listFieldNames
        result = listFieldNames(None)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
