from src.main.app import main

def test_e2e_app():
    # Call our main() app
    response = main()

    # We can assert a 200 success response
    assert response.status_code == 200