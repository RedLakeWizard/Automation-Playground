from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


def test_successful_login_redirects_to_dashboard(page: Page):
    login = LoginPage(page)
    dashboard = DashboardPage(page)

    login.open()
    login.login("test_user", "secret123")

    #Assert URL and dashboard content
    expect(page).to_have_url(DashboardPage.URL)
    dashboard.assert_on_page(username="test_user")


def test_invalid_password_shows_error(page: Page):
    login = LoginPage(page)

    login.open()
    login.login("test_user", "wrongpassword")

    #Stays on login and shows error
    expect(page).to_have_url(LoginPage.URL)
    expect(login.error_message).to_be_visible()
    expect(login.error_message).to_have_text("Invalid username or password")


def test_unknown_user_shows_error(page: Page):
    login = LoginPage(page)

    login.open()
    login.login("theghostofchristmaspast", "Ilovethegrinch9999")

    expect(page).to_have_url(LoginPage.URL)
    expect(login.error_message).to_be_visible()
    expect(login.error_message).to_have_text("Invalid username or password")


def test_empty_credentials_shows_error(page: Page):
    login = LoginPage(page)

    login.open()
    #Submit without filling
    login.login("", "")

    expect(page).to_have_url(LoginPage.URL)
    expect(login.error_message).to_be_visible()
    expect(login.error_message).to_have_text("Invalid username or password")


def test_dashboard_not_accessible_without_login(page: Page):
    dashboard = DashboardPage(page)

    #Go directly to dashboard
    page.goto(DashboardPage.URL)

    #Should redirect back to login
    expect(page).to_have_url(LoginPage.URL)


def test_logout_returns_to_login_and_blocks_dashboard(page: Page):
    login = LoginPage(page)
    dashboard = DashboardPage(page)

    #Log in
    login.open()
    login.login("test_user", "secret123")
    dashboard.assert_on_page(username="test_user")

    #Guess what
    dashboard.logout()

    #Back to login
    expect(page).to_have_url(LoginPage.URL)
    login.assert_on_page()

    #Try to access dashboard again after logout
    page.goto(DashboardPage.URL)
    expect(page).to_have_url(LoginPage.URL)
