import logging
from selenium.webdriver.common.by import By

from pages.login_and_signup_page import LoginAndSignUpPageClass

logger = logging.getLogger(__name__)

class TestSignup:

    def test_valid_sign_up(self, get_driver, signup_data):
        login_and_signup_page = LoginAndSignUpPageClass(get_driver)
        login_and_signup_page.navigate_to_url("https://www.automationexercise.com/")
        login_and_signup_page.enter_signup_details(
        name=signup_data["name"],
        email_address=signup_data["email_address"],
    )
        login_and_signup_page.enter_account_information(
        title=signup_data["title"],
        password=signup_data["password"],
        day=signup_data["date_of_birth"]["day"],
        month=signup_data["date_of_birth"]["month"],
        year=signup_data["date_of_birth"]["year"],
        first_name=signup_data["address"]["first_name"],
        last_name=signup_data["address"]["last_name"],
        company=signup_data["address"]["company"],
        address=signup_data["address"]["address"],
        address_2=signup_data["address"]["address_2"],
        country=signup_data["address"]["country"],
        state=signup_data["address"]["state"],
        city=signup_data["address"]["city"],
        zipcode=signup_data["address"]["zipcode"],
        mobile_number=signup_data["address"]["mobile_number"],
        subscribe_newsletter=signup_data["subscribe_newsletter"],
        receive_special_offers=signup_data["receive_special_offers"],
    )
        login_and_signup_page.create_account()
        assert login_and_signup_page.is_account_created(), f"Account has been successfully created"
