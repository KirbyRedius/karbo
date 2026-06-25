# karbo

Official Python SDK for the [KarboAI](https://karboai.com) Bot API.

<!-- ─────────────────────────  EN  ────────────────────────── -->
<a id="en"></a>
<details open>
<summary><strong>🇬🇧 English</strong></summary>

### 📚 Full documentation

The complete, always up-to-date reference lives in two places:

* **Source & changelog** — [github.com/KirbyRedius/karbo](https://github.com/KirbyRedius/karbo)
* **API & guides** — [docs.karboai.com](https://docs.karboai.com)

The snippets below are a quick taste. Refer to the docs for every
endpoint, every field, error codes, rate limits, and the full inline-
buttons reference.

### Install

```bash
pip install -U karbo
```

### Hello bot

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

### Inline buttons

Attach a `List[List[Button]]` to any message. Rows are the outer list,
columns within a row are the inner list. Up to **10 rows × 5 columns,
30 buttons total** per message.

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
        await bot.send_message(
            press.chat_id, "Paid!", reply_to=press.message_id,
        )
```

Available pieces (see [docs.karboai.com](https://docs.karboai.com)
for the full reference):

* **Styles** — `ButtonStyle`, `Gradient` (horizontal / vertical /
  diagonal / radial), shapes `rectangle` / `circle` / `capsule`.
* **Interactions** — `TapInteraction` (default) or
  `SwipeInteraction(text, fill_color)` (drag-to-confirm).
* **Animations** — `Pulse`, `Neon`, `Glitch`, `Outline` (up to 4 per
  button, no duplicate kinds).
* **Particles** — `SparkParticles`, `ConfettiParticles`,
  `HeartParticles`, `PixelParticles`, `SmokeParticles` (one per
  button, `color` + `intensity` 1-5).

### Models & errors

`BotInfo`, `Message`, `SentMessage`, `User`, `Member`, `Author`,
`AvatarFrame`, `MessageReaction`, `ButtonPress`.

Exceptions all inherit from `karbo.KarboError`:
`AuthenticationError`, `ForbiddenError`, `NotFoundError`,
`ValidationError`, `RateLimitError`, `APIError`.

### License

MIT

</details>

<!-- ─────────────────────────  RU  ────────────────────────── -->
<a id="ru"></a>
<details>
<summary><strong>🇷🇺 Русский</strong></summary>

### 📚 Полная документация

Актуальный и полный референс живёт в двух местах:

* **Исходники и changelog** — [github.com/KirbyRedius/karbo](https://github.com/KirbyRedius/karbo)
* **API и гайды** — [docs.karboai.com](https://docs.karboai.com)

Здесь — только короткие примеры для старта. За полным списком
эндпоинтов, описанием полей, кодами ошибок, лимитами и описанием
inline-кнопок — иди в доку.

### Установка

```bash
pip install -U karbo
```

### Минимальный бот

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

### Inline-кнопки

Прикрепляются к сообщению как `List[List[Button]]`: внешний список —
строки, внутренний — кнопки в строке. До **10 строк × 5 колонок,
30 кнопок всего** на одно сообщение.

```python
import karbo as k

await bot.send_message(
    chat_id,
    "Подтвердить оплату?",
    buttons=[
        [
            k.Button(
                "pay", "Оплатить",
                style=k.ButtonStyle(color="#22C55E", shape="capsule"),
                animations=[k.Pulse(speed_ms=900)],
                particles=k.SparkParticles(color="#FFD54F"),
            ),
            k.Button(
                "cancel", "Отмена",
                style=k.ButtonStyle(color="#1F2937", shape="capsule"),
            ),
        ],
    ],
)

@ws.on_button_pressed
async def on_press(press: k.ButtonPress):
    if press.button_id == "pay":
        await bot.send_message(
            press.chat_id, "Оплачено!", reply_to=press.message_id,
        )
```

Доступные блоки (полный референс — на [docs.karboai.com](https://docs.karboai.com)):

* **Стили** — `ButtonStyle`, `Gradient` (`horizontal` / `vertical` /
  `diagonal` / `radial`), формы `rectangle` / `circle` / `capsule`.
* **Взаимодействия** — `TapInteraction` (по умолчанию) или
  `SwipeInteraction(text, fill_color)` (свайп-подтверждение).
* **Анимации** — `Pulse`, `Neon`, `Glitch`, `Outline` (до 4 на кнопку,
  без дублей по kind).
* **Партиклы** — `SparkParticles`, `ConfettiParticles`,
  `HeartParticles`, `PixelParticles`, `SmokeParticles` (одна
  конфигурация на кнопку, параметры — `color` и `intensity` 1-5).

### Модели и ошибки

`BotInfo`, `Message`, `SentMessage`, `User`, `Member`, `Author`,
`AvatarFrame`, `MessageReaction`, `ButtonPress`.

Все исключения наследуют от `karbo.KarboError`:
`AuthenticationError`, `ForbiddenError`, `NotFoundError`,
`ValidationError`, `RateLimitError`, `APIError`.

### Лицензия

MIT

</details>
