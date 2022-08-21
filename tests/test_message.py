from unittest.mock import AsyncMock

import pytest
from dotenv import load_dotenv

# from handlers.message import start_command, help_command


# @pytest.mark.asyncio
# class TestMessage:
#     # load_dotenv()
#     # async def test_start_command(self):
#     #     message = AsyncMock(text='/start')
#     #     await start_command(message)
#
#     async def test_help_command(self):
#         text = '/help'
#         message_mock = AsyncMock(text=text)
#         await help_command(message=message_mock)
#         message_mock.answer.asser_called_with(text)