from unittest import TestCase
from lxml import etree

from footprints.main.viaf import VIAFRecord


class VIAFRecordTest(TestCase):

    valid_record = '''<?xml version="1.0"  encoding="UTF-8"?>
        <ns2:VIAFCluster xmlns="http://viaf.org/viaf/terms#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:owl="http://www.w3.org/2002/07/owl#"
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:void="http://rdfs.org/ns/void#"
                xmlns:ns2="http://viaf.org/viaf/terms#">
            <ns2:viafID>844120</ns2:viafID>
            <ns2:mainHeadings>
                <ns2:data>
                    <ns2:sources>
                        <ns2:s>NLI</ns2:s>
                        <ns2:sid>NLI|000396016</ns2:sid>
                    </ns2:sources>
                </ns2:data>
                <ns2:data>
                    <ns2:text>Abudarham, David ben Joseph</ns2:text>
                    <ns2:sources>
                        <ns2:s>LC</ns2:s>
                        <ns2:sid>LC|n  86845383</ns2:sid>
                    </ns2:sources>
                </ns2:data>
            </ns2:mainHeadings>
            <ns2:birthDate>1300</ns2:birthDate>
            <ns2:deathDate>14</ns2:deathDate>
        </ns2:VIAFCluster>'''

    incomplete_record = '''<?xml version="1.0"  encoding="UTF-8"?>
        <ns2:VIAFCluster xmlns="http://viaf.org/viaf/terms#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:owl="http://www.w3.org/2002/07/owl#"
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:void="http://rdfs.org/ns/void#"
                xmlns:ns2="http://viaf.org/viaf/terms#">
            <ns2:viafID>844120</ns2:viafID>
            <ns2:mainHeadings>
                <ns2:data>
                    <ns2:sources>
                        <ns2:s>NLI</ns2:s>
                        <ns2:sid>NLI|000396016</ns2:sid>
                    </ns2:sources>
                </ns2:data>
            </ns2:mainHeadings>
        </ns2:VIAFCluster>'''

    def setUp(self):
        self.valid_root = etree.fromstring(self.valid_record)
        self.incomplete_root = etree.fromstring(self.incomplete_record)

    def test_get_name(self):
        self.assertEquals(VIAFRecord.get_name(self.valid_root),
                          'Abudarham, David ben Joseph')
        self.assertIsNone(VIAFRecord.get_name(self.incomplete_root))

    def test_birth_date(self):
        self.assertEquals(VIAFRecord.get_birth_date(self.valid_root), '1300')
        self.assertIsNone(VIAFRecord.get_birth_date(self.incomplete_root))

    def test_death_date(self):
        self.assertEquals(VIAFRecord.get_death_date(self.valid_root), '14')
        self.assertIsNone(VIAFRecord.get_death_date(self.incomplete_root))
