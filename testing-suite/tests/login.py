def test_successful_login(page):
    # go to login
    page.goto("http://localhost:5000/login")

    # fill in credentials
    page.fill("#username", "test_user")
    page.fill("#password", "secret123")
    page.click("#login-btn")

    # assert redirect to dashboard
    assert page.url.endswith("/dashboard")

    # assert welcome message
    welcome = page.text_content("#welcome-msg")
    assert "test_user" in welcome
