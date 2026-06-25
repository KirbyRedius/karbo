# karbo

Official Python SDK for the [KarboAI](https://karboai.com) Bot API.

## Installation

```bash
pip install -U karbo
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
| `send_message(chat_id, content, *, reply_to=None, images=None, buttons=None)` | Send a message with optional images and inline buttons (`SentMessage`) |
| `upload_image(file_path)` | Upload a local image, returns its URL (`str`) |
| `get_message(chat_id, message_id)` | Get a specific message (`Message`) |
| `get_chat_members(chat_id, *, limit=100, offset=0, community_id=None)` | List chat members (`list[Member]`) |
| `get_user(user_id)` | Get user profile (`User`) |
| `get_user_in_community(user_id, community_id)` | Get user profile in a community (`User`) |
| `leave_chat(chat_id)` | Leave a chat |
| `kick_user(chat_id, user_id)` | Kick a user (requires helper role) |

#### Sending images

```python
url = await bot.upload_image("photo.jpg")
await bot.send_message(chat_id, "Check this out!", images=[url])

# Send multiple images (up to 10 per message)
urls = [await bot.upload_image(p) for p in ["a.png", "b.png"]]
await bot.send_message(chat_id, "", images=urls)
```

#### Inline buttons (new in 0.5.0)

Inline buttons are attached to a message as a `List[List[Button]]` —
the outer list is rows, the inner list is columns within a row. Server
limits: up to 10 rows, 5 buttons per row, 30 buttons total.

```python
import karbo as k

await bot.send_message(
    chat_id,
    "Confirm payment?",
    buttons=[
        [
            k.Button(
                "pay", "Pay",
                style=k.ButtonStyle(color="#22C55E", shape="capsule"),
                animations=[k.Pulse(speed_ms=900)],
                particles=k.SparkParticles(color="#FFD54F"),
            ),
            k.Button(
                "cancel", "Cancel",
                style=k.ButtonStyle(color="#1F2937", shape="capsule"),
            ),
        ],
    ],
)

@ws.on_button_pressed
async def on_press(press: k.ButtonPress):
    if press.button_id == "pay":
        await bot.send_message(press.chat_id, "Paid!", reply_to=press.message_id)
```

##### Styles

`ButtonStyle(color, text_color, gradient, shape, corner_radius)` — base
appearance. `shape` is one of `"rectangle"` / `"circle"` / `"capsule"`.

Add a `Gradient(start, end, direction)` for a two-stop fill.
`direction` is one of `"horizontal"`, `"vertical"`, `"diagonal"`,
`"radial"`.

##### Interactions

* `TapInteraction()` (default) — single tap fires the press event.
* `SwipeInteraction(text, fill_color)` — drag left-to-right to confirm.
  The button fills with `fill_color` and shows `text` mid-swipe.

##### Animations

Up to 4 animations per button, no duplicates of the same kind:

* `Pulse(speed_ms)` — soft scale up-down.
* `Neon(color, blur)` — coloured glow around the button.
* `Glitch(intensity_px, frequency_ms)` — periodic RGB-shift jitter.
* `Outline(color, thickness_px, corner_radius)` — static border.

##### Particles

Tap-burst effect. Pick one type per button:

`SparkParticles`, `ConfettiParticles`, `HeartParticles`,
`PixelParticles`, `SmokeParticles` — each takes `color` and
`intensity` (1..5).

### `KarboBotWS(token, *, ws_url="https://api.karboai.com")`

WebSocket client for real-time events.

```python
ws = karbo.KarboBotWS(BOT_TOKEN)

@ws.on_message
async def handler(message: karbo.Message):
    ...

@ws.on_button_pressed
async def pressed(press: karbo.ButtonPress):
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
- **`ButtonPress`** — `chat_id`, `message_id`, `button_id`, `user_id`, `community_id`, `interaction`

### Exceptions

All inherit from `karbo.KarboError`:

- `AuthenticationError` — invalid token (401)
- `ForbiddenError` — no permission (403)
- `NotFoundError` — resource not found (404)
- `ValidationError` — bad request (400, also returned for invalid `inline_buttons` payloads)
- `RateLimitError` — too many requests (429), has `.retry_after`
- `APIError` — other HTTP errors, has `.status` and `.body`

## License

MIT
