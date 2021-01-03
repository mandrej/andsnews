# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import main
import unittest


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        self.test = [
            # '/api/get/bucket_info',
            # '/api/counters',
            # '/api/exif/IMG_0284.jpg',
            '/api/exif/DSC_6349_972_01.jpg',
        ]

    def test(self):
        for url in self.test:
            print('testing ', url)
            response = self.app.get(url)
            assert response.status_code == 200
            if response.is_json:
                print(response.get_json())
            else:
                print(response.data)

# no need to run server!
# (andsnews) $ python -m unittest api/test_app.py
