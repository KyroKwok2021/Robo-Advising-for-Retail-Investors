from discord import Intents, Client, Message
import generate_signals
import datetime


def get_weekday(date_str):
    '''
    Example:
    get_weekday('2024-05-01')
    >> 'Wednesday'
    '''
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    weekday_num = date.weekday()
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday = weekday_names[weekday_num]
    return weekday


def map_signal(x):
    if x > 0:
        return 'Long'
    elif x < 0: 
        return 'Short'
    else:
        return 'None'
    

def format_row(headers, values):
    text = ''
    for header, value in zip(headers, values):
        if 'signal' in header.lower():
            value = '**'+map_signal(value)+'**'
        text += f"{header}: {value}\n"
    text += "\n"
    return text


def format_data(df, num_row=1):
    df = df.tail(num_row).round(2)
    text = ''
    for i in df.index:
        text += '**'+str(i)+'**'
        text += '\n'
        headers = df.loc[i].index.tolist()
        values = df.loc[i].values.tolist()
        text += format_row(headers, values)
    return text


def get_signals():
    Signal_Generator = generate_signals.run()
    return Signal_Generator.df_info


intents = Intents.default()
intents.message_content = True # NOQA
client = Client(intents=intents)
df_info = get_signals()

@client.event
async def on_ready():
    print(f'{client.user.name} is running')

    messsage_signals = format_data(df_info, 1)

    CHANNEL_ID = int('YOUR_CHANNEL_ID')
    channel = client.get_channel(CHANNEL_ID)
    lastest_messages = [message async for message in channel.history(limit=1)][0]
    if len(lastest_messages.content) != 0 and lastest_messages is not None and lastest_messages.content[2:12] in str(df_info.index[-1]):
        print(lastest_messages.content)
        print(str(df_info.index[-1]))
        print('No update data')
        return 
    
    await channel.send(messsage_signals)
    

@ client.event
async def on_message(Message):
    if Message.author == client.user:
        return
    
    channel = Message.channel
    message = str(Message.content)

    if message[0] != '!':
        await channel.send('Wrong notation')
        return
    
    message = message[1:]
    if 'close' in message.lower():
        await client.close()
    # Get the df_into.tail()
    num_row = int(message[:2])
    messsage_signals = format_data(df_info, num_row)
    await channel.send(messsage_signals)

    
VIXF_TOKEN = 'YOUR_PRIVATE_TOKEN'
client.run(token=VIXF_TOKEN)
