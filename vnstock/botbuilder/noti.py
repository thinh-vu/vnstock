import requests
import json
from typing import Union, Dict
from vnstock.core.utils.env import get_path_delimiter

class Messenger:
    def __init__(self, platform:str, channel:Union[str, None], token_key:Union[str, int]):
        """
        Initialize a Messenger object with the platform, channel, and token key.

        Args:
            platform (str): Name of the messaging platform, e.g., 'slack', 'telegram', 'lark'.
            channel (str): Name of the target channel in Slack e.g., '#market_news' or Telegram group id e.g '-1001439492355'.
            token_key (str): 
                Slack: Bot token (start with 'xoxb-..') or user token (start with 'xoxp-..').
                Telegram: Token key for the Telegram bot.
                Lark: Webhook token for the Lark Botbuilder. For example, it's 1234hbhfdt56456ljkfftdre4587 in the webhook url https://botbuilder.larksuite.com/api/trigger-webhook/1234hbhfdt56456ljkfftdre4587 from Lark Botbuilder Flow.
        
        Returns:
            Messenger object.
        """
        self.platform = platform
        self.channel = channel
        self.token_key = token_key
        self._validation()

    def _validation(self):
        """
        Validate the Messenger object's attributes.

        Returns:
            raise ValueError if any of the attributes are invalid.
            return raw value if all attributes are valid.
        """
        if self.platform not in ['slack', 'telegram', 'lark']:
            raise ValueError('Invalid platform. Supported platforms are "slack", "telegram", and "lark".')
        if self.token_key is None:
            raise ValueError('Token key is required for messaging!')
        if self.platform == 'slack' and self.token_key[0:4] != 'xoxb' and self.token_key[0:4] != 'xoxp':
            raise ValueError('Invalid token key for Slack. Bot token must start with "xoxb-" and user token must start with "xoxp-".')
        
        if self.platform == 'slack':
            if self.channel is None:
                raise ValueError('Channel name is required for Slack messaging!')
            elif self.channel[0] != '#':
                raise ValueError('Channel name must start with "#" for Slack messaging!')
        elif self.platform == 'telegram':
            if self.channel is None:
                raise ValueError('Channel name is required for Telegram messaging!')
            elif self.channel[0] != '-':
                raise ValueError('Channel name must start with "-" for Telegram messaging!. For example, "-1001439492355".')
        elif self.platform == 'lark':
            if self.channel is not None:
                raise ValueError('Channel name is not required for Lark messaging!')


    def send_message(self, message:str, file_path:Union[str, None]=None, title:Union[str, None]=None):
        """
        Send a message to a channel or group using the specified platform.
        """
        if self.platform == 'slack':
            if file_path is not None:
                return self._slack_file(message, file_path, title)
            else:
                return self._slack_message(message)
        
        elif self.platform == 'telegram':
            if file_path is not None:
                return self._telegram_photo(message, file_path)
            else:
                return self._telegram_message(message)

    def _slack_file(self, text_comment, file_path, title=None):
        """
        Send a file to a Slack channel using either a bot or a user token.

        Args:
            text_comment (str): Text comment for the file.
            file_path (str): Path to the target file.
            title (str): Optional title for the file.

        Returns:
            dict: Response from the Slack API in JSON format.
        """      
        file_name = file_path.split(get_path_delimiter())[-1]
        file_type = file_name.split('.')[-1]
        file_bytes = open(file_path, 'rb').read()
        url = 'https://slack.com/api/files.upload'
        payload = {
            'token': self.token_key,
            'filename': file_name,
            'channels': self.channel,
            'filetype': file_type,
            'initial_comment': text_comment,
            'title': title
        }
        r = requests.post(url, payload, files={'file': file_bytes})
        return r.json()
    
    def _slack_message(self, message):
        """
        Send a message to a Slack channel using either a bot or a user token.

        Args:
            message (str): Text message for the file.

        Returns:
            dict: Response from the Slack API in JSON format.
        """

        header = {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer {}'.format(self.token_key)
        }
        payload = json.dumps({
            "channel": "{}".format(self.channel),
            "text": "{}".format(message)
        })
        response = requests.post('https://slack.com/api/chat.postMessage', data=payload, headers=header)

        return response.json()

    def _telegram_photo(self, message, file_path):
        """
        Send a photo to a Telegram group.

        Args:
            message (str): Your text message.
            file_path (str): Path of the file/photo to send via Telegram.

        Returns:
            object: Response object from the Telegram API.
        """
        file_type = file_path.split('.')[-1]
        if file_type not in ['jpg', 'jpeg', 'png', 'webp']:
            raise ValueError('Invalid file type. Telegram only supports JPG, JPEG, PNG, and WEBP formats.')
        file_name = file_path.split(get_path_delimiter())[-1][0]
        files = [('photo', (file_name, open(file_path, 'rb'), f'image/{file_type}'))]
        url = 'https://api.telegram.org/bot{}/sendPhoto'.format(self.token_key)
        payload = {'chat_id': self.channel, 'caption': message}
        response = requests.post(url, headers={}, data=payload, files=files)
        return response
         
    def _telegram_message(self, message):
        """
        Send a message to a Telegram group.

        Args:
            message (str): Your text message.

        Returns:
            object: Response object from the Telegram API.
        """
        url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(self.token_key, self.channel, message) # thêm chữ bot trước token so với code cũ
        response = requests.post(url)
        return response.json()

    def _lark_message(self, message:str, payload:Union[Dict, None]=None):
        """
        Send a message to a Lark Botbuilder Webhook.

        Args:
            message (str): Your text message.
            payload (dict): Optional payload for the message.
        Returns:
            object: Response object from the Lark API.
        """
        # validate payload shoule be None or dict
        url = f'https://botbuilder.larksuite.com/api/trigger-webhook/{self.token_key}'
        if payload is None:
            payload = {'content' : message}
        else:
            payload = message
        response = requests.post(url, json=payload)
        return response.json()