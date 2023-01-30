from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ProductData:
    """
    A data class to hold converted product info
    """
    product_id: str
    product_category: str
    product_description: str
    product_images: dict
    prices: List[dict]

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_category": self.product_category,
            "product_description": self.product_description,
            "product_images": self.product_images,
            "prices": self.prices,
        }


@dataclass(frozen=True)
class RawProduct:
    """A data class to hold raw product info received from repositories"""
    id: str
    category: str
    description: str
    images: dict
    prices: List[dict]
