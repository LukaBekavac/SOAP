import json
import logging
import random
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, AlbumNotDownload, VideoNotDownload
from typing import List

from instagrapi.types import Media, UserShort

from ComplexEncoder import ComplexEncoder


class SessionCreator:
    def __init__(self, username, password, session_file='session.json', request_timeout=10):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.client = Client()
        self.client.delay_range = [1, 3]
        self.logger = logging.getLogger(__name__)
        self.request_timeout = request_timeout

    def login(self):
        try:
            self.client.load_settings(self.session_file)
            self.client.login(self.username, self.password)
            self.client.get_timeline_feed()  # Check if session is valid
            self.logger.info("Logged in successfully using session.")
        except (LoginRequired, Exception):
            self.logger.info("Session is invalid, logging in with username and password.")
            self.client.login(self.username, self.password)
            self.save_session()

    def save_session(self):
        self.client.dump_settings(self.session_file)
        self.logger.info(f"Session saved to {self.session_file}.")

    def explore_reels(self, amount: int = 10, last_media_pk: int = 0) -> List[Media]:
        return self.client.explore_reels(amount, last_media_pk)

    def explore_page(self):
        return self.client.explore_page()

    def media_info_v1(self, media_pk: int):
        return self.client.media_info_v1(media_pk)

    def reels_timeline_media(
            self, collection_pk: str, amount: int = 10, last_media_pk: int = 0
    ) -> List[Media]:
        return self.client.reels_timeline_media(collection_pk, amount, last_media_pk)

    #download photo posts
    def photo_download(self, media_pk: int, folder: Path = "") -> Path:
        return self.client.photo_download(media_pk, folder)

    def save_and_print_explore_reels(self, amount: int = 10, last_media_pk: int = 0):
        reels = self.explore_reels(amount, last_media_pk)
        print(reels)

        # Save the response to a JSON file
        with open('data/explore_reels2.json', 'w') as f:
            json.dump([media.dict() for media in reels], f, cls=ComplexEncoder)

    def clip_download(self, media_pk: int, folder: Path = "") -> str:
        return self.client.clip_download(media_pk, folder)

    def album_download(self, media_pk: int, folder: Path = "") -> List[Path]:
        media = self.media_info_v1(media_pk)
        assert media.media_type == 8, "Must been album"
        paths = []
        for resource in media.resources:
            filename = f"{media.user.username}_{resource.pk}"
            if resource.media_type == 1:
                paths.append(
                    self.photo_download_by_url(resource.thumbnail_url, filename, folder)
                )
            elif resource.media_type == 2:
                paths.append(
                    self.video_download_by_url(resource.video_url, filename, folder)
                )
            else:
                raise AlbumNotDownload(
                    'Media type "{resource.media_type}" unknown for album (resource={resource.pk})'
                )
        return paths

    def photo_download_by_url(
            self, url: str, filename: str = "", folder: Path = ""
    ) -> Path:
        url = str(url)
        fname = urlparse(url).path.rsplit("/", 1)[1]
        filename = "%s.%s" % (filename, fname.rsplit(".", 1)[1]) if filename else fname
        path = Path(folder) / filename
        response = requests.get(url, stream=True, timeout=self.request_timeout)
        response.raise_for_status()
        with open(path, "wb") as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        return path.resolve()

    def media_like(self, media_id: str, revert: bool = False) -> bool:
        """
        Like a media

        Parameters
        ----------
        media_id: str
            Unique identifier of a Media
        revert: bool, optional
            If liked, whether or not to unlike. Default is False

        Returns
        -------
        bool
            A boolean value
        """
        assert self.user_id, "Login required"
        media_id = self.media_pk(media_id)
        data = {
            "inventory_source": "media_or_ad",
            "media_id": media_id,
            "radio_type": "wifi-none",
            "is_carousel_bumped_post": "false",
            "container_module": "feed_timeline",
            "feed_position": str(random.randint(0, 6)),
        }
        name = "unlike" if revert else "like"
        result = self.private_request(
            f"media/{media_id}/{name}/", self.with_action_data(data)
        )
        return result["status"] == "ok"

    def media_id(self, media_pk: str) -> str:
        """
        Get full media id

        Parameters
        ----------
        media_pk: str
            Unique Media ID

        Returns
        -------
        str
            Full media id

        Example
        -------
        2277033926878261772 -> 2277033926878261772_1903424587
        """
        media_id = str(media_pk)
        if "_" not in media_id:
            assert media_id.isdigit(), (
                    "media_id must been contain digits, now %s" % media_id
            )
            user = self.media_user(media_id)
            media_id = "%s_%s" % (media_id, user.pk)
        return media_id

    def media_user(self, media_pk: str) -> UserShort:
        """
        Get author of the media

        Parameters
        ----------
        media_pk: str
            Unique identifier of the media

        Returns
        -------
        UserShort
            An object of UserShort
        """
        return self.media_info_v1(media_pk).user

    def video_download_by_url(
            self, url: str, filename: str = "", folder: Path = ""
    ) -> Path:
        url = str(url)
        fname = urlparse(url).path.rsplit("/", 1)[1]
        filename = "%s.%s" % (filename, fname.rsplit(".", 1)[1]) if filename else fname
        path = Path(folder) / filename
        response = requests.get(url, stream=True, timeout=self.request_timeout)
        response.raise_for_status()
        try:
            content_length = int(response.headers.get("Content-Length"))
        except TypeError:
            print(
                """
                The program detected an mis-formatted link, and hence can't download it.
                This problem occurs when the URL is passed into
                    'video_download_by_url()' or the 'clip_download_by_url()'.
                The raw URL needs to be re-formatted into one that is recognizable by the methods.
                Use this code: url=self.cl.media_info(self.cl.media_pk_from_url('insert the url here')).video_url
                You can remove the 'self' from the code above if needed.
                """
            )
            raise Exception("The program detected an mis-formatted link.")
        file_length = len(response.content)
        if content_length != file_length:
            raise VideoNotDownload(
                f'Broken file "{path}" (Content-length={content_length}, but file length={file_length})'
            )
        with open(path, "wb") as f:
            f.write(response.content)
            f.close()
        return path.resolve()
