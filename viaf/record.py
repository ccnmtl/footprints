import urllib
from urllib2 import URLError

from lxml import etree
from lxml.etree import ParseError


class VIAFRecord(object):

    '''Access to linked names for the same entity across the world's major '''
    '''name authority files, including national and regional variations in '''
    '''language, character set, and spelling.'''
    '''https://platform.worldcat.org/api-explorer/VIAF'''

    namespaces = {'ns2': 'http://viaf.org/viaf/terms#'}

    def __init__(self, name, birth, death):
        self.name = name
        self.birth_date = birth
        self.death_date = death

    @classmethod
    def query_document(cls, root, q):
        nodes = root.xpath(q, namespaces=cls.namespaces)
        return nodes[0].text if len(nodes) > 0 else None

    @classmethod
    def get_birth_date(cls, root):
        return cls.query_document(root, '//ns2:birthDate')

    @classmethod
    def get_death_date(cls, root):
        return cls.query_document(root, '//ns2:deathDate')

    @classmethod
    def get_name(cls, root):
        q = '//ns2:mainHeadings/ns2:data/ns2:sources/ns2:s[text()="LC"]'
        nodes = root.xpath(q, namespaces=cls.namespaces)
        if len(nodes) < 1:
            return None

        # possible alternate name query, using code "a" or "t"
        # q = '//ns2:datafield[@dtype="MARC21"]/ns2:subfield[@code="a"]'

        return nodes[0].getparent().getprevious().text

    @classmethod
    def fetch(cls, identifier):
        try:
            base_url = 'http://www.viaf.org/viaf'
            url = '{}/{}/'.format(base_url, identifier)
            root = etree.parse(urllib.urlopen(url))

            name = cls.get_name(root)
            if name is None:
                return None

            birth_date = cls.get_birth_date(root)
            death_date = cls.get_death_date(root)
            return VIAFRecord(name=name, birth=birth_date, death=death_date)
        except (URLError, ParseError):
            # url is unreachable or identifier is invalid
            return None
