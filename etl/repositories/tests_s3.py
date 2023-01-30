import unittest

from etl.core.dto import ProductData
from etl.repositories.s3 import S3ProductRepo


# NOTE: These tests are just showcases. Mocking the behaviour of boto3 is not the point here.

class DummyRepository:
    def __init__(self):
        self.s = {}

    def put_object(self, Body, Bucket, Key):
        self.s[Key] = Body


class TestS3ProductRepo(unittest.TestCase):
    """
    NOTE: These tests are just showcases. Mocking the behaviour of boto3 is not the point here.
    """

    def test_save_empty_data(self):
        repo = S3ProductRepo("my-bucket", DummyRepository())
        repo.save(data=[], name="?")

    def test_save_items(self):
        fake = DummyRepository()
        p1 = ProductData("1", "cat", "desc", {"image_1": "img_1"}, [{"currency": "EUR", "value": 1001}])
        repo = S3ProductRepo("my-bucket", s3_client=fake)
        repo.save(data=[p1], name="file-1.json")
        self.assertEqual(len(fake.s), 1)
        self.assertIn("file-1.json", fake.s)
