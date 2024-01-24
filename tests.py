import json
import multiprocessing
import unittest
import time
from faker import Faker
import requests
from api.main import exe

DOMAIN = "localhost"
PORT = 8000

fake = Faker()
HOST = f"http://{DOMAIN}:{PORT}"

process = multiprocessing.Process(target=exe, kwargs={"host": DOMAIN, "port": PORT})


def setUpModule():
    process.start()
    time.sleep(3)


def tearDownModule():
    process.terminate()


class BookTestGET(unittest.TestCase):
    def setUp(self):
        requests.get(f"{HOST}/reset")

    def test_get_book_valid_id(self):
        book_id = 1
        response = requests.get(f"{HOST}/books/book/{book_id}")
        self.assertEqual(response.status_code, 200)

    def test_get_book_invalid_id(self):
        book_id = 99999
        response = requests.get(f"{HOST}/books/book/{book_id}")
        self.assertEqual(response.status_code, 404)

    def test_get_book_invalid_id_type(self):
        book_id = "invalid-id"
        response = requests.get(f"{HOST}/books/book/{book_id}")
        self.assertEqual(response.status_code, 422)


class BookTestPOST(unittest.TestCase):
    def setUp(self):
        requests.get(f"{HOST}/reset")

    def test_create_book_full_data(self):
        data = {
            "title": fake.sentence(),
            "publish_year": int(fake.year()),
            "author_id": fake.random_int(min=1, max=100),
            "barcode": fake.bothify(text='#######')
        }
        response = requests.post(f"{HOST}/books/", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertDictContainsSubset(data, response.json())

    def test_create_book_minimal_data(self):
        data = {
            "title": fake.sentence(),
            "publish_year": fake.year(),
            "author_id": fake.random_int(min=1, max=100)
        }
        response = requests.post(f"{HOST}/books/", json=data)
        self.assertEqual(response.status_code, 422)

    def test_create_book_invalid_data(self):
        data = {
            "title": fake.sentence(),
            "publish_year": "invalid-year",
            "author_id": fake.random_int(min=1, max=100),
            "barcode": fake.bothify(text='#######')
        }
        response = requests.post(f"{HOST}/books/", json=data)
        self.assertEqual(response.status_code, 422)

    def test_create_book_missing_required_fields(self):
        data = {
            "publish_year": fake.year(),
            "author_id": fake.random_int(min=1, max=100)
        }
        response = requests.post(f"{HOST}/books/", json=data)
        self.assertEqual(response.status_code, 422)


class BookTestPUT(unittest.TestCase):
    def setUp(self):
        requests.get(f"{HOST}/reset")

    def test_update_book(self):
        data = {
                "title": "New Hello, WORLD123!",
                "publish_year": 1999,
                "author_id": 8,
                "barcode": "13322334"
                }

        response = requests.put(f"{HOST}/books/1", data=json.dumps(data))
        expected_status_code = 200
        expected_data = {
                          "title": "New Hello, WORLD123!",
                          "publish_year": 1999,
                          "author_id": 8,
                          "barcode": "13322334"
                        }

        self.assertEqual(expected_status_code, response.status_code)
        self.assertDictEqual(expected_data, response.json())

    def test_update_book_not_found(self):
        data = {
            "title": "New Hello, WORLD!",
            "publish_year": 1999,
            "author_id": 8,
            "barcode": "ajdhalhjd"
        }

        response = requests.put(f"{HOST}/books/55555555", data=json.dumps(data))
        expected_status_code = 404
        expected_data = {
                         "detail": "Book not found"
                         }

        self.assertEqual(expected_status_code, response.status_code)
        self.assertDictEqual(expected_data, response.json())


class BookTestDELETE(unittest.TestCase):
    def setUp(self):
        requests.get(f"{HOST}/ping")

    def test_delete_book(self):
        book_id = fake.random_int(min=1, max=20)
        response = requests.delete(f"{HOST}/books/{book_id}")
        expected_status_code = 204

        self.assertEqual(expected_status_code, response.status_code)

    def test_delete_book_not_found(self):
        book_id = 555555555
        response = requests.delete(f"{HOST}/books/{book_id}")
        expected_status_code = 204

        self.assertEqual(expected_status_code, response.status_code)


if __name__ == "__main__":
    unittest.main()
