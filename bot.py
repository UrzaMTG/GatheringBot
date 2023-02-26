import configparser
import asyncio

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

broadcaster = ''
bot_name = ''
app_id = ''
app_secret = ''

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

multi = ''

def import_config():
    config = configparser.ConfigParser()
    config.read('botSettings.ini')
    global broadcaster, bot_name, app_id, app_secret
    broadcaster = config['BaseInfo']['channel']
    bot_name = config['BaseInfo']['bot_name']
    app_id = config['Secrets']['app_id']
    app_secret = config['Secrets']['app_secret']

async def on_ready(ready_event: EventData):
    print('Bot initialized, joining channel')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(broadcaster)

# Event handler for incoming messages in chat
def handle_message(message: ChatMessage):
    # Commands that can be used by any user
    if message.text.startswith('!multi'):
        if len(multi) > 0:
            message.chat.send_message(message.room, f"Watch everyone I'm playing with at {multi} (make sure to mute all but one stream)")
        else:
            message.chat.send_message(message.room, f"Multi not yet set, poke @{broadcaster}")

    # Commands that can be used by VIPs and Mods
    if not (message.user.vip or message.user.mod or message.user.display_name == broadcaster): return

    # Commands that can be used by Mods
    if not (message.user.mod or message.user.display_name == broadcaster): return

    #Commands that can only be used by the broadcaster
    if (message.user.display_name != broadcaster): return

    if message.text.startswith('!setmulti'):
        global multi
        multi_users = message.text[10:]
        multi = f'https://kadgar.net/live/{multi_users}'
        message.chat.send_message(message.room, f'Multi set to {multi}')

# Async entry
async def main():
    import_config()

    twitch = await Twitch(app_id, app_secret)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    # create chat instance
    chat = await Chat(twitch)

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)

    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, handle_message)

    # you can directly register commands and their handlers, this will register the !reply command


    # we are done with our setup, lets start this bot up!
    chat.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()


if __name__ == '__main__':
    asyncio.run(main())