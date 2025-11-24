import pytest
from playwright.sync_api import Page, expect


@pytest.mark.parametrize(
    "username,password,redirect",
    [
        ("test_user", "secret123", "/account/dashboard"),
        ("admin", "adminpass", "/admin/dashboard"),
    ],
)
def test_login_success(page: Page, username: str, password: str, redirect: str):
    page.goto("http://localhost:5000/auth/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#login-btn")
    expect(page).to_have_url(f"http://localhost:5000{redirect}")


def test_login_failure_shows_error(page: Page):
    page.goto("http://localhost:5000/auth/login")
    page.fill("#username", "baduser")
    page.fill("#password", "badpass")
    page.click("#login-btn")
    expect(page).to_have_url("http://localhost:5000/auth/login")
    expect(page.locator("#login-error")).to_contain_text("Invalid username or password")
