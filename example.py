"""Example: echo bot — replies with text echo + an image to every message."""

import asyncio

import karbo

BOT_TOKEN = "your-token-here"


async def main():
    async with karbo.KarboBot(BOT_TOKEN) as bot:
        ws = karbo.KarboBotWS(BOT_TOKEN)

        me = await bot.get_me()
        print(f"Logged in as {me.name} ({me.bot_id}) — status: {me.status}")

        @ws.on_connect
        async def on_connect():
            print("WebSocket connected — listening for messages...")

        @ws.on_disconnect
        async def on_disconnect():
            print("WebSocket disconnected")

        @ws.on_message
        async def on_message(message: karbo.Message):
            if message.user_id == me.bot_id:
                return

            author_name = message.author.nickname if message.author else "Unknown"
            print(f"[{message.chat_id}] {author_name}: {message.content}")

            echo = await bot.send_message(
                message.chat_id,
                f"Echo: {message.content}",
                reply_to=message.message_id,
            )
            print(f"  → Echo reply: {echo.message_id}")

            url = await bot.upload_image("karbo.png")
            pic = await bot.send_message(
                message.chat_id,
                images=[url],
            )
            print(f"  → Image sent: {pic.message_id}")

        try:
            await ws.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            await ws.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
