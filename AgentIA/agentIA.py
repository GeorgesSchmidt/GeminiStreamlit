import os
import sys


class GeminiClient:
    def __init__(self, chat):
        self.chat = chat

    def ask(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return response.text.strip()


