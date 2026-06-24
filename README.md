# karbo

Official Python SDK for the [KarboAI](https://karboai.com) Bot API.

## Installation

```bash
pip install karbo
```

## Quick Start

```python
import asyncio
import karbo

BOT_TOKEN = "your-bot-token"

async def main():
    bot = karbo.KarboBot(BOT_TOKEN)
    ws = karbo.KarboBotWS(BOT_TOKEN)

    me = await bot.get_me()
    print(f"Bot: {me.name} ({me.bot_id})")

    @ws.on_message
    async def on_message(message: karbo.Message):
        if message.user_id == me.bot_id:
            return
        await bot.send_message(message.chat_id, f"Echo: {message.content}")

    await ws.run_forever()

asyncio.run(main())
```

## API Reference

### `KarboBot(token, *, base_url="https://api.karboai.com")`

Async HTTP client. Use as a context manager or call `.close()` when done.

| Method | Description |
|---|---|
| `get_me()` | Get bot info (`BotInfo`) |
| `send_message(chat_id, content, *, reply_to=None, images=None)` | Send a message with optional images (`SentMessage`) |
| `upload_image(file_path)` | Upload a local image, returns its URL (`str`) |
| `get_message(chat_id, message_id)` | Get a specific message (`Message`) |
| `get_chat_members(chat_id, *, limit=100, offset=0)` | List chat members (`list[Member]`) |
| `get_user(user_id)` | Get user profile (`User`) |
| `get_user_in_community(user_id, community_id)` | Get user profile in a community (`User`) |
| `leave_chat(chat_id)` | Leave a chat |
| `kick_user(chat_id, user_id)` | Kick a user (requires helper role) |

#### Sending images

```python
url = await bot.upload_image("photo.jpg")
await bot.send_message(chat_id, "Check this out!", images=[url])

# Send multiple images
urls = [await bot.upload_image(p) for p in ["a.png", "b.png"]]
await bot.send_message(chat_id, "", images=urls)
```

### `KarboBotWS(token, *, ws_url="https://api.karboai.com")`

WebSocket client for real-time events.

```python
ws = karbo.KarboBotWS(BOT_TOKEN)

@ws.on_message
async def handler(message: karbo.Message):
    ...

@ws.on_connect
async def connected():
    ...

@ws.on_disconnect
async def disconnected():
    ...

await ws.run_forever()
```

### Models

- **`BotInfo`** — `bot_id`, `name`, `status`
- **`Message`** — `message_id`, `chat_id`, `user_id`, `content`, `created_time`, `type`, `reply_message_id`, `author`, `images`
- **`SentMessage`** — `message_id`, `created_time`
- **`User`** — `user_id`, `nickname`, `avatar`, `short_info`, `role`, `app_role`, `panel_color`, `level`, `nickname_color`, `nickname_emoji`, `avatar_frame`, `bubble_id`
- **`Member`** — `user_id`, `nickname`, `avatar`, `role`, `app_role`, `panel_color`, `level`, `nickname_color`, `nickname_emoji`, `avatar_frame`, `member_status`, `is_api_bot`
- **`Author`** — `user_id`, `nickname`, `avatar`, `role`, `app_role`, `panel_color`, `level`, `nickname_color`, `nickname_emoji`, `avatar_frame`
- **`AvatarFrame`** — `frame_id`, `file`
- **`MessageReaction`** — `reaction`, `is_sticker`, `count`, `me`

### Exceptions

All inherit from `karbo.KarboError`:

- `AuthenticationError` — invalid token (401)
- `ForbiddenError` — no permission (403)
- `NotFoundError` — resource not found (404)
- `ValidationError` — bad request (400)
- `RateLimitError` — too many requests (429), has `.retry_after`
- `APIError` — other HTTP errors, has `.status` and `.body`

## License

MIT
