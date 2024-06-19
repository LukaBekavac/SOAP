import os
import logging
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

logger = logging.getLogger()

class InstagramLogin:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.client = Client()

    def login_user(self):
        """
        Attempts to login to Instagram using either the provided session information
        or the provided username and password.
        """

        session = self.client.load_settings("session.json")

        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.client.set_settings(session)
                self.client.login(self.username, self.password)

                # check if session is valid
                try:
                    self.client.get_timeline_feed()
                except LoginRequired:
                    logger.info("Session is invalid, need to login via username and password")

                    old_session = self.client.get_settings()

                    # use the same device uuids across logins
                    self.client.set_settings({})
                    self.client.set_uuids(old_session["uuids"])

                    self.client.login(self.username, self.password)
                login_via_session = True
            except Exception as e:
                logger.info("Couldn't login user using session information: %s" % e)

        if not login_via_session:
            try:
                logger.info("Attempting to login via username and password. username: %s" % self.username)
                if self.client.login(self.username, self.password):
                    login_via_pw = True
            except Exception as e:
                logger.info("Couldn't login user using username and password: %s" % e)

        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")
