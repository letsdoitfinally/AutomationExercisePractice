import logging
import os

import pytest
import time

from models.signup_models import AccountInformation
from pages.cart_page import CartPageClass
from pages.home_page import HomePageClass
from pages.login_and_signup_page import LoginAndSignUpPageClass

logger = logging.getLogger(__name__)

class TestLoginSignup:

    def test_valid_sign_up(self, get_driver, signup_data):
        login_and_signup_page = LoginAndSignUpPageClass(get_driver)
        login_and_signup_page.navigate_to_url("https://www.automationexercise.com/")
        login_and_signup_page.enter_signup_details(
        name=signup_data["name"],
        email_address=signup_data["email_address"],
    )
        account_info = AccountInformation.from_dict(signup_data)
        login_and_signup_page.enter_account_information(account_info)
        login_and_signup_page.create_account()
        assert login_and_signup_page.is_account_created(), f"Account has been successfully created"
        login_and_signup_page.navigate_to_url("https://www.automationexercise.com/")
        name = login_and_signup_page.header_component.get_logged_in_user_name()
        assert  name == f"{signup_data["name"]}",(f"Name of user {signup_data["name"]} "
                                                  f"with which account is created is not appearing in as logged in user {name} ")
        login_and_signup_page.header_component.logout()



    @pytest.mark.parametrize("invalid_login_data",["invalid_email", "invalid_password", "invalid"],indirect=True)
    def test_invalid_login(self, get_driver, invalid_login_data):
        login_and_signup_page = LoginAndSignUpPageClass(get_driver)
        login_and_signup_page.navigate_to_url("https://www.automationexercise.com/")
        login_and_signup_page.login(invalid_login_data['email'], invalid_login_data['password'])
        assert login_and_signup_page.get_login_error_text() == 'Your email or password is incorrect!',\
            "Error message not appearing on login with incorrect password or username"

    def test_signup_while_checkout(self, get_driver):
        pass

    def test_login_while_checkout(self, get_driver):
        home_page =  HomePageClass(get_driver)
        home_page.navigate_to_home_page()
        home_page.add_featured_product_to_cart()
        assert home_page.cart_modal.is_visible()
        home_page.cart_modal.click_view_cart()
        cart_page = CartPageClass(get_driver)
        cart_page.proceed_to_checkout()
        cart_page.click_register_login()
        login_and_signup_page = LoginAndSignUpPageClass(get_driver)
        username = os.getenv("test_username")
        password = os.getenv("test_password")
        if not username or not password:
            raise RuntimeError(
                "Missing test_username or test_password environment variables."
            )
        login_and_signup_page.login(username, password)
        home_page.navigate_to_home_page()
        cart_page.header_component.navigate_to_cart_page()
        cart_page.proceed_to_checkout()













