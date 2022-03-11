# Sample code from offical Flask tutorial:
# https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
# Not implemented yet as no create_app functionality in aat at time of writing
# - Rich, 11th March 2022

###########################################


from aat import create_app


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"
