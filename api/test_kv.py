import unittest


def push_message(recipients, message='', **data):
    """
    Cloud function send
    """
    body = {"recipients": recipients, "message": message}
    if data:
        body["data"] = data

    for k, v in body.items():
        print(k, v)


class TestKv(unittest.TestCase):
    def test_kv(self):
        push_message('12839021830', 'hello', group="tags", value=13)
        push_message('sdsdsdsds', 'hello')


# no need to run server!
# (andsnews) $ python -m unittest api/test_kv.py
