"""
Multi-platform notification and messaging service for bot integration.

Supports sending messages and files to:
- Slack (bot and user tokens)
- Telegram (groups and channels)
- Discord (webhooks)
- Lark (Botbuilder webhooks)

Examples:
    Slack example:
        >>> slack = Messenger('slack', '#general', 'xoxb-...')
        >>> slack.send_message('Alert: Stock price updated!')

    Telegram example:
        >>> telegram = Messenger('telegram', '-1001234567890',
        ...                       'bot_token')
        >>> telegram.send_message('Market update', file_path='chart.png')

    Discord example:
        >>> webhook = 'https://discord.com/api/webhooks/...'
        >>> discord = Messenger('discord', webhook_url=webhook)
        >>> discord.send_message('Trading bot notification',
        ...                       file_path='report.pdf')

    Lark example:
        >>> lark = Messenger('lark', token_key='webhook_token')
        >>> lark.send_message('Daily report')
"""

import os
import json
import base64
from typing import Union, Dict, Optional

import requests

from vnstock.core.utils.env import get_path_delimiter
from vnstock.core.utils.logger import get_logger
from vnstock.core.types import FileTypes

logger = get_logger(__name__)


class Messenger:
    """
    Multi-platform messaging service with unified interface.

    Supports sending text messages and file attachments to 4 major platforms:
    - Slack (Enterprise messaging)
    - Telegram (Mobile-first messaging)
    - Discord (Community platform)
    - Lark (Team collaboration)

    Each platform uses platform-specific validation and API endpoints.

    Attributes:
        SUPPORTED_PLATFORMS: List of supported messaging platforms
        TIMEOUT: Request timeout in seconds
    """

    SUPPORTED_PLATFORMS = ['slack', 'telegram', 'discord', 'lark']
    TIMEOUT = 30  # Request timeout in seconds
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size

    def __init__(
        self,
        platform: str,
        channel: Optional[str] = None,
        token_key: Optional[Union[str, int]] = None,
        webhook_url: Optional[str] = None
    ):
        """
        Initialize Messenger for a specific platform.

        Args:
            platform: Messaging platform ('slack', 'telegram',
                'discord', 'lark')
            channel: Target channel/group identifier:
                - Slack: Channel name with # prefix (e.g., '#general')
                - Telegram: Chat/group ID with - prefix
                  (e.g., '-1001234567890')
                - Discord: None (not required)
                - Lark: None (not required)
            token_key: Authentication token/key:
                - Slack: Bot token (xoxb-) or user token (xoxp-)
                - Telegram: Bot token
                - Discord: None (use webhook_url instead)
                - Lark: Webhook token
            webhook_url: Webhook URL (Discord only)

        Raises:
            ValueError: If platform or credentials are invalid
        """
        self.platform = platform.lower()
        self.channel = channel
        self.token_key = token_key
        self.webhook_url = webhook_url
        self._validate()

    def _validate(self):
        """
        Validate platform-specific configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.platform not in self.SUPPORTED_PLATFORMS:
            platforms_str = ', '.join(self.SUPPORTED_PLATFORMS)
            raise ValueError(
                f"Supported platforms: {platforms_str}. "
                f"Got: {self.platform}"
            )

        # Slack validation
        if self.platform == 'slack':
            if not self.token_key:
                raise ValueError('Slack requires token_key parameter')
            token_str = str(self.token_key)
            if not (token_str.startswith('xoxb-') or
                    token_str.startswith('xoxp-')):
                raise ValueError(
                    'Invalid Slack token. Must start with xoxb- or xoxp-'
                )
            if not self.channel or not self.channel.startswith('#'):
                raise ValueError(
                    'Slack channel must start with # (e.g., #general)'
                )

        # Telegram validation
        elif self.platform == 'telegram':
            if not self.token_key:
                raise ValueError('Telegram requires token_key parameter')
            if not self.channel or not self.channel.startswith('-'):
                raise ValueError(
                    'Telegram channel must start with - '
                    '(e.g., -1001234567890)'
                )

        # Discord validation
        elif self.platform == 'discord':
            if not self.webhook_url:
                raise ValueError(
                    'Discord requires webhook_url parameter'
                )
            if not self.webhook_url.startswith(
                'https://discord.com/api/webhooks/'
            ):
                raise ValueError(
                    'Invalid Discord webhook URL format'
                )

        # Lark validation
        elif self.platform == 'lark':
            if not self.token_key:
                raise ValueError('Lark requires token_key parameter')
            if self.channel is not None:
                raise ValueError(
                    'Lark messaging does not require a channel'
                )

    def _get_file_mime_type(self, file_path: str) -> str:
        """
        Determine MIME type based on file extension.

        Args:
            file_path: Path to the file

        Returns:
            MIME type string or 'application/octet-stream' for unknown types
        """
        extension = file_path.split('.')[-1].lower()
        return FileTypes.get_mime_type(extension)

    def _encode_file_to_base64(self, file_path: str) -> str:
        """
        Encode file to base64 string.

        Args:
            file_path: Path to the file

        Returns:
            Base64 encoded string

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If error reading file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {e}")

    def send_message(
        self,
        message: str,
        file_path: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict:
        """
        Send message with optional file attachment.

        Args:
            message: Message text to send
            file_path: Path to file to attach (optional)
            title: File title/name for attachment (optional)

        Returns:
            API response dictionary with status and data

        Raises:
            FileNotFoundError: If file_path does not exist
            ValueError: If file is too large (>50MB)
        """
        try:
            if file_path is not None:
                # Validate file before sending
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")

                file_size = os.path.getsize(file_path)
                if file_size > self.MAX_FILE_SIZE:
                    raise ValueError(
                        f"File too large. Max size: "
                        f"{self.MAX_FILE_SIZE / 1024 / 1024}MB, "
                        f"got: {file_size / 1024 / 1024:.2f}MB"
                    )

                # Send with file
                if self.platform == 'slack':
                    return self._slack_file(message, file_path, title)
                elif self.platform == 'telegram':
                    result = self._telegram_photo(message, file_path)
                    if isinstance(result, dict):
                        return result
                    return result.json()
                elif self.platform == 'discord':
                    return self._discord_file(message, file_path, title)
                else:  # lark
                    return self._lark_file(message, file_path, title)
            else:
                # Send text only
                if self.platform == 'slack':
                    return self._slack_message(message)
                elif self.platform == 'telegram':
                    return self._telegram_message(message)
                elif self.platform == 'discord':
                    return self._discord_message(message)
                else:  # lark
                    return self._lark_message(message)

        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Validation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 400
            }
        except Exception as e:
            logger.error(f"Unexpected error in send_message: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'status_code': 500
            }

    def _slack_file(self, text_comment: str, file_path: str,
                    title: Optional[str] = None) -> Dict:
        """
        Send file to Slack channel.

        Args:
            text_comment: Comment text with file
            file_path: Path to file
            title: Optional file title

        Returns:
            Slack API response
        """
        file_name = file_path.split(get_path_delimiter())[-1]
        file_type = file_name.split('.')[-1]

        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        url = 'https://slack.com/api/files.upload'
        payload = {
            'token': self.token_key,
            'filename': file_name,
            'channels': self.channel,
            'filetype': file_type,
            'initial_comment': text_comment,
            'title': title
        }

        response = requests.post(
            url,
            data=payload,
            files={'file': file_bytes},
            timeout=self.TIMEOUT
        )
        return response.json()

    def _slack_message(self, message: str) -> Dict:
        """
        Send text message to Slack channel.

        Args:
            message: Message text

        Returns:
            Slack API response
        """
        headers = {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {self.token_key}'
        }
        payload = json.dumps({
            "channel": self.channel,
            "text": message
        })

        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            data=payload,
            headers=headers
        )
        return response.json()

    def _telegram_photo(self, message: str,
                        file_path: str) -> requests.Response:
        """
        Send photo to Telegram group.

        Args:
            message: Caption text
            file_path: Path to image file

        Returns:
            Telegram API response

        Raises:
            ValueError: If file format not supported
        """
        extension = file_path.split('.')[-1].lower()
        if extension not in ['jpg', 'jpeg', 'png', 'webp']:
            raise ValueError(
                f'Telegram only supports JPG, JPEG, PNG, WEBP. '
                f'Got: {extension}'
            )

        file_name = file_path.split(get_path_delimiter())[-1]
        files = [
            (
                'photo',
                (
                    file_name,
                    open(file_path, 'rb'),
                    f'image/{extension}'
                )
            )
        ]

        url = (
            f'https://api.telegram.org/bot{self.token_key}/sendPhoto'
        )
        payload = {
            'chat_id': self.channel,
            'caption': message
        }

        response = requests.post(
            url,
            data=payload,
            files=files,
            timeout=self.TIMEOUT
        )
        return response.json()

    def _telegram_message(self, message: str) -> Dict:
        """
        Send text message to Telegram group.

        Args:
            message: Message text

        Returns:
            Telegram API response
        """
        url = (f'https://api.telegram.org/bot{self.token_key}/'
               f'sendMessage?chat_id={self.channel}&text={message}')
        response = requests.post(url)
        return response.json()

    def _discord_message(self, message: str) -> Dict:
        """
        Send text message to Discord channel via webhook.

        Args:
            message: Message text

        Returns:
            Discord API response dictionary
        """
        try:
            if not isinstance(self.webhook_url, str):
                raise ValueError('Discord webhook_url must be a string')

            payload = {'content': message}
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if response.text else {}
            }
        except (ValueError, requests.exceptions.RequestException) as e:
            logger.error(f"Discord message error: {e}")
            status_code = 500
            if isinstance(e, requests.exceptions.RequestException):
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
            return {
                'success': False,
                'error': str(e),
                'status_code': status_code
            }

    def _discord_file(
        self,
        message: str,
        file_path: str,
        title: Optional[str] = None
    ) -> Dict:
        """
        Send file to Discord channel via webhook.

        Supports all file types. Discord will embed media files
        (images, videos) directly in the message.

        Args:
            message: Message text or description
            file_path: Path to file to upload
            title: Optional file title (displayed as filename)

        Returns:
            Discord API response dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If error reading file
        """
        try:
            if not isinstance(self.webhook_url, str):
                raise ValueError('Discord webhook_url must be a string')

            file_name = file_path.split(get_path_delimiter())[-1]
            display_name = title or file_name

            with open(file_path, 'rb') as f:
                files = {
                    'file': (display_name, f)
                }
                data = {'content': message}

                response = requests.post(
                    self.webhook_url,
                    data=data,
                    files=files,
                    timeout=self.TIMEOUT
                )
                response.raise_for_status()

                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response': response.json() if response.text else {}
                }

        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Discord file error: {e}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 400
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord API error: {e}")
            status_code = 500
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            return {
                'success': False,
                'error': str(e),
                'status_code': status_code
            }
        except IOError as e:
            logger.error(f"File read error: {e}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 400
            }

    def _lark_message(self, message: str,
                      payload: Optional[Dict] = None) -> Dict:
        """
        Send message to Lark Botbuilder webhook.

        Args:
            message: Message text
            payload: Optional custom payload dictionary

        Returns:
            Lark API response
        """
        url = (f'https://botbuilder.larksuite.com/api/trigger-webhook/'
               f'{self.token_key}')

        if payload is None:
            payload = {'message': message}

        response = requests.post(url, json=payload)
        return response.json()

    def _lark_file(self, message: str, file_path: str,
                   title: Optional[str] = None) -> Dict:
        """
        Send file to Lark via webhook as base64 encoded data.

        Args:
            message: Message text
            file_path: Path to file
            title: Optional file title

        Returns:
            Lark API response

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If error reading file
        """
        try:
            # Get file information
            file_name = file_path.split(get_path_delimiter())[-1]
            extension = file_name.split('.')[-1].lower()
            mime_type = self._get_file_mime_type(file_path)

            # Encode file to base64
            base64_content = self._encode_file_to_base64(file_path)

            # Get file size
            file_size = os.path.getsize(file_path)

            # Prepare and send payload
            url = (f'https://botbuilder.larksuite.com/api/trigger-webhook/'
                   f'{self.token_key}')
            payload = {
                'message': message,
                'file': {
                    'name': file_name,
                    'title': title or file_name,
                    'content': base64_content,
                    'mime_type': mime_type,
                    'extension': extension,
                    'size': file_size,
                    'encoding': 'base64'
                }
            }

            response = requests.post(url, json=payload)
            return response.json()

        except (FileNotFoundError, IOError) as e:
            logger.error(f"File error: {e}")
            return {
                'error': True,
                'message': str(e),
                'status_code': 400
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'error': True,
                'message': f'Unexpected error: {str(e)}',
                'status_code': 500
            }
