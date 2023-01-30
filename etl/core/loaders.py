# The `xml2json service` converts any xml data to json considering the transformation rules
import logging
import traceback

import xmltodict

from etl.exceptions import XmlInvalidStructure, ConvertException

logger = logging.getLogger(__name__)


class ProductXmlLoader:
    """
    Loads the raw xml to a list of data-objects.

    raises a CoreException if (id, price) is not present in the raw xml. Other fields are not required and
    will be returned as zero-values.
    """

    def __init__(self, data_cls):
        self.ProductDataCls = data_cls

    def load(self, raw):
        logger.info("loading raw xml to raw objects...")
        try:
            data = xmltodict.parse(raw)
        except Exception as e:
            raise ConvertException(e)
        try:
            items = data["nsx:items"]["nsx:item"]
        except KeyError as e:
            raise XmlInvalidStructure(str(e))

        # raw xml could be a single item or list of items
        if not isinstance(items, list):
            items = [items]

        all_products = []
        for item in items:
            # extract images from raw xml
            tmp_images = self._load_images(item)
            # extract prices
            tmp_prices = self._load_prices(item)
            tmp_desc = self._load_description(item)
            tmp_category = self._load_category(item)
            tmp_id = self._load_id(item)

            # Create a new RawProduct Data Object
            product = self.ProductDataCls(tmp_id, tmp_category, tmp_desc, tmp_images, tmp_prices)
            all_products.append(product)

        return all_products

    def _load_images(self, item):
        try:
            images = item["nsx:images"]["nsx:image"]
        except KeyError as e:
            return {}

        # If the product has only 1 image
        if not isinstance(images, list):
            images = [images]
        # a dict like:  {"1": "http://example.com/image.jpg"}
        return {img["@type"]: img["@url"] for img in images}

    def _load_prices(self, item):
        try:
            prices = item["nsx:prices"]["nsx:price"]
        except KeyError as e:
            raise XmlInvalidStructure(f"the product item needs at least one price - {str(item)}")

        # If the product has only 1 price
        if not isinstance(prices, list):
            prices = [prices]

        result = []
        for price in prices:
            result.append({"currency": price["nsx:currency"], "value": price["nsx:value"]})
        return result

    def _load_description(self, item):
        try:
            return item["nsx:description"]
        except KeyError as e:
            return ""

    def _load_category(self, item):
        try:
            return item["nsx:category"]
        except KeyError as e:
            return ""

    def _load_id(self, item):
        try:
            return item["@id"]
        except KeyError as e:
            raise XmlInvalidStructure(f"id is required - {str(item)}")
