#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom import replace_identifiers, utils
from deid.tests.common import create_recipe, get_file
from deid.utils import get_installdir

global generate_uid


class TestRemoveAction(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def run_remove_test(self, Field):
        print(f"Test REMOVE standard tags in format {Field}")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[Field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertNotIn(Field, outputfile)

    def test_remove_standard_tags_1(self):
        self.run_remove_test("(0010,0010)")  # PatientName in DICOM format

    def test_remove_standard_tags_2(self):
        self.run_remove_test("00100010")  # PatientName in hex format

    def test_remove_standard_tags_3(self):
        self.run_remove_test("PatientName")  # PatientName in keyword format

    def test_remove_private_tags_test(self):
        """RECIPE RULE
        REMOVE (0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)
        """
        print(f"Test REMOVE private tag in format (0033,'MITRA OBJECT UTF8 ATTRIBUTES 1.0', 1E)")
        dicom_file = get_file(self.dataset)

        Field = "(0033,'MITRA OBJECT UTF8 ATTRIBUTES 1.0',1E)"
        field_dicom = '0x0033101E'
        actions = [
            {"action": "REMOVE", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field_dicom].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )
        outputfile = utils.dcmread(result[0])

        self.assertEqual(1, len(result))
        self.assertNotIn('(0033,101E)', outputfile)

if __name__ == "__main__":
    unittest.main()