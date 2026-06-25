# karbo

Official Python SDK for the [KarboAI](https://karboai.com) Bot API.

[![PyPI](https://img.shields.io/pypi/v/karbo)](https://pypi.org/project/karbo/) [![Python](https://img.shields.io/pypi/pyversions/karbo)](https://pypi.org/project/karbo/) [![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Full API reference: [**docs.karboai.com**](https://docs.karboai.com)

---

## 🇺🇸 English

### Install

```bash
pip install -U karbo
```

Requires Python 3.10+.

### Get a token

Open the KarboAI app → settings → **Developer Panel** → create a bot.
Each bot has its own token used for both HTTP and WebSocket.

### Run a bot

A bot is two pieces: an HTTP client (`KarboBot`) for sending things,
and a WebSocket client (`KarboBotWS`) for receiving incoming messages
and button presses. Both share the same token.

```python
import asyncio
import karbo

BOT_TOKEN = "your-bot-token"


async def main():
    bot = karbo.KarboBot(BOT_TOKEN)
    ws = karbo.KarboBotWS(BOT_TOKEN)

    me = await bot.get_me()
    print(f"Logged in as {me.name} ({me.bot_id})")

    @ws.on_message
    async def on_message(message: karbo.Message):
        # Skip our own messages.
        if message.user_id == me.bot_id:
            return
        await bot.send_message(
            message.chat_id,
            f"Echo: {message.content}",
            reply_to=message.message_id,
        )

    await ws.run_forever()


asyncio.run(main())
```

### Send a message

```python
await bot.send_message(chat_id, "Hello!")

# Reply to a specific message:
await bot.send_message(chat_id, "Got it", reply_to=message.message_id)
```

### Send an image

Upload the file first to get a URL, then attach it to a message.
Up to **10 images** per message; max **20 MB** per file
(`.jpg`, `.png`, `.webp`, `.gif`).

```python
url = await bot.upload_image("photo.jpg")
await bot.send_message(chat_id, "Look at this!", images=[url])

# Multiple images:
urls = [await bot.upload_image(p) for p in ["a.png", "b.png", "c.png"]]
await bot.send_message(chat_id, "Album", images=urls)
```

### Inline buttons

Attach interactive buttons under any message. The structure is
`List[List[Button]]`: the outer list is **rows**, the inner is
**columns within a row**. Limits per message: 10 rows, 5 buttons per
row, 30 buttons total.

#### A minimal example

```python
import karbo as k

await bot.send_message(
    chat_id,
    "Choose an option:",
    buttons=[
        [
            k.Button("yes", "Yes", style=k.ButtonStyle(color="#22C55E")),
            k.Button("no",  "No",  style=k.ButtonStyle(color="#EF4444")),
        ],
    ],
)
```

Each button needs a unique **id** (1-64 chars, `[A-Za-z0-9_.-]`) — that's
what comes back in the press event.

#### Receiving presses

Use the `@ws.on_button_pressed` decorator. The payload tells you
who pressed (`user_id`), in which chat (`chat_id`), in which
community (`community_id`), and how (`interaction`: `"tap"` or
`"swipe"`).

```python
@ws.on_button_pressed
async def handler(press: karbo.ButtonPress):
    if press.button_id == "yes":
        await bot.send_message(press.chat_id, f"OK!", reply_to=press.message_id)

    # Look up who pressed if you need their nickname/avatar:
    user = await bot.get_user(press.user_id)
    print(f"{user.nickname} pressed {press.button_id}")
```

#### Styles, shapes, gradients

```python
k.Button(
    "fancy", "Pay $5",
    style=k.ButtonStyle(
        gradient=k.Gradient(start="#A78BFA", end="#FF7AB6", direction="diagonal"),
        text_color="#FFFFFF",
        shape="capsule",          # "rectangle" | "circle" | "capsule"
        corner_radius=14,          # only used by "rectangle"
    ),
)
```

`Gradient.direction` is one of `"horizontal"`, `"vertical"`,
`"diagonal"`, `"radial"`.

#### Swipe-to-confirm

For destructive or important actions, ask the user to swipe instead
of tap. The button shows the swipe text and fills with `fill_color`
as the user drags.

```python
k.Button(
    "delete", "Delete",
    style=k.ButtonStyle(color="#1F2937"),
    interaction=k.SwipeInteraction(
        text="Swipe to delete",
        fill_color="#EF4444",
    ),
)
```

In the press handler check `press.interaction == "swipe"` to confirm.

#### Animations

Up to 4 per button, one of each kind. Animations are visual only —
they don't affect the press event.

```python
animations=[
    k.Pulse(speed_ms=900),                       # soft scale up-down
    k.Neon(color="#22D3EE", blur=16),            # coloured glow halo
    k.Glitch(intensity_px=3, frequency_ms=2500), # periodic CRT-style flash
    k.Outline(color="#FFD54F", thickness_px=2, corner_radius=12),  # border
]
```

#### Particles on tap

Optional one-shot burst when the user taps the button.

```python
particles=k.ConfettiParticles(color="#FFD54F", intensity=4)
```

Available types: `SparkParticles`, `ConfettiParticles`,
`HeartParticles`, `PixelParticles`, `SmokeParticles`.
`intensity` is 1-5.

#### Kitchen-sink button

Everything together:

```python
k.Button(
    "premium", "✨ Go Pro",
    style=k.ButtonStyle(
        gradient=k.Gradient(start="#A78BFA", end="#FF7AB6", direction="diagonal"),
        text_color="#FFFFFF",
        shape="capsule",
    ),
    interaction=k.SwipeInteraction(text="Swipe to confirm", fill_color="#22C55E"),
    animations=[
        k.Pulse(speed_ms=1100),
        k.Neon(color="#A78BFA", blur=16),
    ],
    particles=k.ConfettiParticles(color="#FFD54F", intensity=5),
)
```

### Errors

All exceptions inherit from `karbo.KarboError`:

| Exception | Meaning |
|---|---|
| `AuthenticationError` | Invalid bot token (401) |
| `ForbiddenError` | Not allowed to do this (403) |
| `NotFoundError` | Resource missing (404) |
| `ValidationError` | Bad request body — e.g. invalid `inline_buttons` schema (400) |
| `RateLimitError` | Too many requests (429); has `.retry_after` seconds |
| `APIError` | Other HTTP errors; has `.status` and `.body` |

### License

MIT

---

## 🇷🇺 Русский

### Установка

```bash
pip install -U karbo
```

Нужен Python 3.10+.

### Получить токен

Открой приложение KarboAI → настройки → **Developer Panel** → создай
бота. У каждого бота свой токен, который используется и для HTTP, и
для WebSocket.

### Запустить бота

Бот состоит из двух частей: HTTP-клиент (`KarboBot`) для отправки и
WebSocket-клиент (`KarboBotWS`) для получения входящих сообщений и
нажатий на кнопки. Оба используют один и тот же токен.

```python
import asyncio
import karbo

BOT_TOKEN = "your-bot-token"


async def main():
    bot = karbo.KarboBot(BOT_TOKEN)
    ws = karbo.KarboBotWS(BOT_TOKEN)

    me = await bot.get_me()
    print(f"Залогинились как {me.name} ({me.bot_id})")

    @ws.on_message
    async def on_message(message: karbo.Message):
        # Пропускаем свои же сообщения.
        if message.user_id == me.bot_id:
            return
        await bot.send_message(
            message.chat_id,
            f"Echo: {message.content}",
            reply_to=message.message_id,
        )

    await ws.run_forever()


asyncio.run(main())
```

### Отправить сообщение

```python
await bot.send_message(chat_id, "Привет!")

# Ответ на конкретное сообщение:
await bot.send_message(chat_id, "Понял", reply_to=message.message_id)
```

### Отправить картинку

Сначала загружаешь файл и получаешь URL, потом прикрепляешь его к
сообщению. До **10 картинок** на сообщение, **20 МБ** на файл
(`.jpg`, `.png`, `.webp`, `.gif`).

```python
url = await bot.upload_image("photo.jpg")
await bot.send_message(chat_id, "Зацени!", images=[url])

# Несколько картинок:
urls = [await bot.upload_image(p) for p in ["a.png", "b.png", "c.png"]]
await bot.send_message(chat_id, "Альбом", images=urls)
```

### Inline-кнопки

Прикрепляются под любое сообщение бота. Структура —
`List[List[Button]]`: внешний список — **ряды**, внутренний —
**кнопки в ряду**. Лимиты: 10 рядов, 5 в ряду, 30 кнопок на
сообщение.

#### Минимальный пример

```python
import karbo as k

await bot.send_message(
    chat_id,
    "Выбери вариант:",
    buttons=[
        [
            k.Button("yes", "Да",  style=k.ButtonStyle(color="#22C55E")),
            k.Button("no",  "Нет", style=k.ButtonStyle(color="#EF4444")),
        ],
    ],
)
```

У каждой кнопки должен быть уникальный **id** (1-64 символа,
`[A-Za-z0-9_.-]`) — именно он придёт в событии нажатия.

#### Получение нажатий

Используй декоратор `@ws.on_button_pressed`. В payload'е есть кто
нажал (`user_id`), в каком чате (`chat_id`), в каком community
(`community_id`) и как именно (`interaction`: `"tap"` или
`"swipe"`).

```python
@ws.on_button_pressed
async def handler(press: karbo.ButtonPress):
    if press.button_id == "yes":
        await bot.send_message(press.chat_id, "ОК!", reply_to=press.message_id)

    # Если нужно имя/аватар нажавшего:
    user = await bot.get_user(press.user_id)
    print(f"{user.nickname} нажал {press.button_id}")
```

#### Стили, формы, градиенты

```python
k.Button(
    "fancy", "Оплатить 500₽",
    style=k.ButtonStyle(
        gradient=k.Gradient(start="#A78BFA", end="#FF7AB6", direction="diagonal"),
        text_color="#FFFFFF",
        shape="capsule",          # "rectangle" | "circle" | "capsule"
        corner_radius=14,          # используется только для "rectangle"
    ),
)
```

`Gradient.direction` — `"horizontal"`, `"vertical"`, `"diagonal"`
или `"radial"`.

#### Swipe-подтверждение

Для важных или необратимых действий проси юзера свайпнуть, а не
тапнуть. Кнопка показывает текст и заливается цветом `fill_color`
по мере того как палец тянет thumb.

```python
k.Button(
    "delete", "Удалить",
    style=k.ButtonStyle(color="#1F2937"),
    interaction=k.SwipeInteraction(
        text="Свайп для удаления",
        fill_color="#EF4444",
    ),
)
```

В обработчике нажатия проверяй `press.interaction == "swipe"`.

#### Анимации

До 4 анимаций на кнопку, без дублей по kind. Анимации только
визуальные — на событие нажатия не влияют.

```python
animations=[
    k.Pulse(speed_ms=900),                       # мягкое «дыхание»
    k.Neon(color="#22D3EE", blur=16),            # цветное свечение
    k.Glitch(intensity_px=3, frequency_ms=2500), # CRT-вспышка с RGB-сдвигом
    k.Outline(color="#FFD54F", thickness_px=2, corner_radius=12),  # рамка
]
```

#### Партиклы при тапе

Опциональная вспышка частиц при тапе.

```python
particles=k.ConfettiParticles(color="#FFD54F", intensity=4)
```

Доступные типы: `SparkParticles`, `ConfettiParticles`,
`HeartParticles`, `PixelParticles`, `SmokeParticles`.
`intensity` — 1..5.

#### «Всё сразу»

Полная конфигурация:

```python
k.Button(
    "premium", "✨ Премиум",
    style=k.ButtonStyle(
        gradient=k.Gradient(start="#A78BFA", end="#FF7AB6", direction="diagonal"),
        text_color="#FFFFFF",
        shape="capsule",
    ),
    interaction=k.SwipeInteraction(text="Свайп для подтверждения", fill_color="#22C55E"),
    animations=[
        k.Pulse(speed_ms=1100),
        k.Neon(color="#A78BFA", blur=16),
    ],
    particles=k.ConfettiParticles(color="#FFD54F", intensity=5),
)
```

### Ошибки

Все исключения наследуют от `karbo.KarboError`:

| Исключение | Когда возникает |
|---|---|
| `AuthenticationError` | Неверный токен бота (401) |
| `ForbiddenError` | Нет прав на это действие (403) |
| `NotFoundError` | Ресурс не найден (404) |
| `ValidationError` | Битый body — например, неверная схема `inline_buttons` (400) |
| `RateLimitError` | Слишком много запросов (429), есть поле `.retry_after` (секунды) |
| `APIError` | Прочие HTTP-ошибки, есть `.status` и `.body` |

### Лицензия

MIT
