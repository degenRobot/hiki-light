from chat import start
import asyncio

async def _testChat() :
    await start(inputs = {})

# Create an event loop
loop = asyncio.get_event_loop()

# Use the event loop to run _testChat
loop.run_until_complete(_testChat())