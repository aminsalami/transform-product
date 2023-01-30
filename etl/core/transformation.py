import logging
from typing import List

from etl.core.dto import ProductData, RawProduct

logger = logging.getLogger(__name__)


class ProductTransformer:
    TargetCls = ProductData

    def transform(self, products: List[RawProduct]) -> List[ProductData]:
        """receives a list of product items from previous stage, convert them to ProductData object"""
        logger.info("Transforming raw objects...")
        result = []
        for p in products:
            transformed_images = self._transform_images(p.images)
            product = self.TargetCls(p.id, p.category, p.description, transformed_images, p.prices)
            result.append(product)
        logger.info("%s objects transformed", len(result))
        return result

    def _transform_images(self, images) -> dict:
        prefix = "image_"
        res = {}
        max_num = 0
        for key, value in images.items():
            try:
                if max_num < int(key):
                    max_num = int(key)
            except ValueError:
                pass
            res[prefix + key] = value

        # fill the gap
        for i in range(1, max_num):
            if str(i) not in images:
                res[prefix + str(i)] = None

        return res
