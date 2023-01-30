import unittest

from etl.core.dto import RawProduct
from etl.exceptions import CoreException, XmlInvalidStructure
from etl.core.loaders import ProductXmlLoader
from etl.core.transformation import ProductTransformer


# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logger = logging.getLogger(__name__)

class TestProductXmlLoader(unittest.TestCase):

    def test_invalid_format_xml(self):
        c = ProductXmlLoader(data_cls=RawProduct)
        with self.assertRaises(XmlInvalidStructure):
            c.load("""
            <nsx:item id="1">
		        <nsx:category>Jeans</nsx:category>
		    </nsx:item>
            """)

    def test_empty_xml(self):
        c = ProductXmlLoader(data_cls=RawProduct)
        with self.assertRaises(CoreException):
            c.load("")

    def test_id_is_required(self):
        c = ProductXmlLoader(data_cls=RawProduct)
        with self.assertRaises(XmlInvalidStructure):
            c.load("""
            <nsx:item>
                <nsx:category>Jeans</nsx:category>
                </nsx:item>
            """)

    def test_valid_1_item(self):
        """Test if convertor returns exactly 1 data object"""
        xml = """
        <nsx:items>
            <nsx:item id="1">
            <nsx:category>Jeans</nsx:category>
                <nsx:description>Bootleg Front Washed</nsx:description>
                <nsx:images>
                    <nsx:image type="1" url="https://sample.com/img/2445456_Image_1.jpg"/>
                    <nsx:image type="3" url="https://sample.com/img/2445456_Image_3.jpg"/>
                </nsx:images>
                <nsx:prices>
                    <nsx:price>
                        <nsx:currency>EUR</nsx:currency>
                        <nsx:value>10</nsx:value>
                    </nsx:price>
                    <nsx:price>
                        <nsx:currency>DKK</nsx:currency>
                        <nsx:value>101.2</nsx:value>
                    </nsx:price>
                </nsx:prices>
            </nsx:item>        
        </nsx:items>
"""
        c = ProductXmlLoader(data_cls=RawProduct)
        data = c.load(xml)
        self.assertEqual(1, len(data))
        d = data[0]
        self.assertEqual(d.id, "1")
        self.assertEqual(len(d.images), 2)
        self.assertEqual(len(d.prices), 2)
        self.assertEqual(d.prices[0]["value"], "10")
        self.assertEqual(d.prices[1]["value"], "101.2")

    def test_valid_2_items(self):
        """Test if we have received multiple products as xml file"""

        xml = """
        <nsx:items>
        <nsx:item id="100">
            <nsx:category>PinkFloyd</nsx:category>
            <nsx:description>Dark Side of the Moon</nsx:description>
            <nsx:images>
                <nsx:image type="1" url="https://sample.com/img/2445456_Image_1.jpg"/>
            </nsx:images>
            <nsx:prices>
                <nsx:price>
                    <nsx:currency>DKK</nsx:currency>
                        <nsx:value>101.2</nsx:value>
                </nsx:price>
            </nsx:prices>
        </nsx:item>

        <nsx:item id="101">
            <nsx:category>PinkFloyd-2</nsx:category>
            <nsx:description>Dark Side of the Moon-2</nsx:description>
            <nsx:images>
                <nsx:image type="2" url="https://sample.com/img/2445456_Image_2.jpg"/>
            </nsx:images>
            <nsx:prices>
                <nsx:price>
                    <nsx:currency>DKK</nsx:currency>
                    <nsx:value>101.2</nsx:value>
                </nsx:price>
                <nsx:price>
                    <nsx:currency>EUR</nsx:currency>
                    <nsx:value>2</nsx:value>
                </nsx:price>
            </nsx:prices>
        </nsx:item>
        </nsx:items>
"""
        c = ProductXmlLoader(data_cls=RawProduct)
        data = c.load(xml)

        self.assertEqual(2, len(data))
        d0 = data[0]
        self.assertEqual(d0.id, "100")
        self.assertEqual(len(d0.images), 1)
        self.assertEqual(len(d0.prices), 1)
        self.assertEqual(d0.prices[0]["value"], "101.2")
        d1 = data[1]
        self.assertEqual(d1.id, "101")
        self.assertEqual(len(d1.images), 1)
        with self.assertRaises(KeyError):
            self.assertIsNone(d1.images["1"])
        self.assertIsNotNone(d1.images["2"])
        self.assertEqual(len(d1.prices), 2)
        self.assertEqual(d1.prices[1]["value"], "2")

    def test_if_field_is_not_present(self):
        xml = """
        <nsx:items>
        <nsx:item id="100">
            <nsx:category>PinkFloyd</nsx:category>
        </nsx:item>
        </nsx:items>
        """
        c = ProductXmlLoader(data_cls=RawProduct)
        with self.assertRaises(XmlInvalidStructure):
            c.load(xml)


class TestProductTransform(unittest.TestCase):
    def test_images_with_non_integer_type(self):
        p = RawProduct("1", "cat", "desc", {"1": "http://bestseller.com/1.gif", "wtf": "http://E-Corp.com/2.gif"}, [])
        t = ProductTransformer()
        dto = t.transform([p])
        self.assertEqual(len(dto), 1)
        self.assertEqual(len(dto[0].product_images), 2)
        self.assertIn("image_1", dto[0].product_images)
        self.assertIn("image_wtf", dto[0].product_images)
        self.assertNotIn("wtf", dto[0].product_images)

    def test_valid_scenario(self):
        p1 = RawProduct(
            "1", "cat", "desc",
            {"1": "http://bestseller.com/1.gif", "3": "http://bestseller.com/3.gif"},
            [{"currency": "EUR", "value": 666}],
        )
        p2 = RawProduct(
            "1001", "", "",
            {"2": "http://bestseller.com/2.gif"},
            [{"currency": "EUR", "value": 666}, {"currency": "IRR", "value": 777}],
        )
        t = ProductTransformer()
        dto = t.transform([p1, p2])
        self.assertEqual(len(dto), 2)

        d1 = dto[0]
        self.assertEqual(len(d1.product_images), 3)
        self.assertEqual(d1.product_images["image_2"], None)
        self.assertIn("image_1", d1.product_images)
        self.assertIn("image_2", d1.product_images)
        self.assertIn("image_3", d1.product_images)
        self.assertEqual(len(d1.prices), 1)
        self.assertEqual(d1.product_id, p1.id)
        self.assertEqual(d1.product_category, p1.category)
        self.assertEqual(d1.product_description, p1.description)

        d2 = dto[1]
        self.assertEqual(len(d2.product_images), 2)
        self.assertEqual(len(d2.prices), 2)
        self.assertEqual(d2.product_images["image_1"], None)
