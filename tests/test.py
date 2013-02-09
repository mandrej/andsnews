__author__ = 'milan'

from webtest import TestApp
from ..main import app

testapp = TestApp(app)

def test_index():
    response = app.get('/complete/Photo/lens')
    assert response.code == 200
