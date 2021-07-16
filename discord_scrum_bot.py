import math
import random
import json
import discord
import requests
from discord.ext import commands

# 88-61 id estimation

DISCORD_TOKEN = 'Njk2NjgwNTg0NDgyNjUyMjYx.XosQWw.mh_IN_BWfm2T0eCaBCVkdzqNHtQ'
YOUTRACK_TOKEN = 'perm:aS5rb3JzdW4=.NzItNQ==.6CBn1SxDlyGq77OdofJ4tYCv2fEhGi'  # https://www.jetbrains.com/help/youtrack/standalone/Manage-Permanent-Token.html
YOUTRACK_URL = 'https://youtrack.ticketland.ru/api/issues/'
HEADERS = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + YOUTRACK_TOKEN,
    'Content-Type': 'application/json'
}

client = commands.Bot(command_prefix='$')

MARKS = {
    '1️⃣': 1,
    '2️⃣': 2,
    '3️⃣': 3,
    '4️⃣': 4,
    '5️⃣': 5,
    '8️⃣': 8,
    '🔟': 10,
    '👻': 13,
    '🤔': 18,
}

TASK_NUMBER = {

}

DICT_MARKS = {

}

title_emoji = ['🚀', '🏎', '🚑', '✈️',
               '🛰', '🎡', '🏝', '⛩',
               '🏔', '🌌', '🛸', '🤺',
               '🏌️', '🤾‍♂️', '🏋️‍♂️',
               '🔥', '🌪', '🍄', '🦜',
               '🦈', '🐳', '🦄', '🐥',
               '🦖', '🐒', '🤞🏻', '🤘🏻',
               '🙏🏻', '💪🏻', '👨🏻‍💻', '🧗🏻',
               '🏄🏻', '🧘🏻', '🤹🏼‍♂️', '🦔']


def get_task(task_number: str):
    url = YOUTRACK_URL + task_number + '?fields=summary,idReadable,description'
    try:
        response = requests.get(url, headers=HEADERS)
        return json.loads(response.text)
    except Exception as e:
        print(e)
    return False


def send_result(result: int, task_number: str):
    url = YOUTRACK_URL + task_number + '?fields=customFields(id,name,value(Estimation))'
    params = json.dumps({
        "customFields":
            [
                {
                    'name': 'Estimation',
                    '$type': 'PeriodIssueCustomField',
                    'value': {'minutes': result * 60}
                }
            ]
    })
    try:
        response = requests.post(url, headers=HEADERS, data=params)
        print(response.text)
        return json.loads(response.text)
    except Exception as e:
        print(e)
    return False


@client.event
async def on_ready():
    print('Bot is ready.')


@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    author = reaction.message.author.id
    if reaction.emoji == '🏁':  # выводим итоговое сообщение с оценками и средним
        s = sum(DICT_MARKS.values())
        count = len(DICT_MARKS)
        print('количество значений в словаре = ' + str(count))

        print(DICT_MARKS)

        average = None
        try:
            average = math.ceil(s / count)
            print('Среднее = ' + str(average))
        except ZeroDivisionError as e:
            print(e)
        if average:
            send_result(average, TASK_NUMBER['task_number'])
            embed = discord.Embed(  # How to do it https://www.youtube.com/watch?v=XKQWxAaRgG0
                title=f'Средняя оценка = {average}',
                description='\n'.join('{} -- {}'.format(value, key) for key, value in DICT_MARKS.items()),
                color=discord.Color.blue()
            )

            await channel.send(embed=embed)
            await reaction.remove(user)
            DICT_MARKS.clear()

    elif user != client.user and reaction.emoji != '🏁':  # если лайк поставлен не ботом то выдавать сообщение о добавлении
        if author == 696680584482652261:  # если автор сообщения бот, то реагировать на эмоджи
            await reaction.remove(user)
            await channel.send(f'{user.name} :white_check_mark:')
            mark = MARKS[reaction.emoji]
            print('mark is ' + str(mark))
            # если голосует один и тот-же человек, то в словарь будет для него перезаписываться а не дублироваться
            DICT_MARKS[user.name] = mark
            # если не бот ставит реакцию то удалить реакцию


# по команде $go + текст истории = выводится текст истории и эмоджики
@client.command()
async def go(ctx, *, arg: str):
    TASK_NUMBER['task_number'] = arg.strip()
    task = get_task(TASK_NUMBER['task_number'])
    embed = discord.Embed(
        title=f"{random.choice(title_emoji)} {task.get('idReadable', arg)} - {task.get('summary', '')}",
        description='Description: ' + str(task.get('description', '')) + '''\nЧтобы поставить оценку - кликните по эмодзи:
                      1️⃣ -- 1 час
                      2️⃣ -- 2 часа
                      3️⃣ -- 3 часа
                      4️⃣ -- 4 часа
                      5️⃣ -- 5 часов
                      8️⃣ -- 8 часов
                      🔟 -- 10 часов
                      👻 -- 13 часов
                      🤔 -- 18 часов
                      🏁 -- посмотреть результаты.''',
        color=discord.Color.blue()
    )

    message = await ctx.send(embed=embed)

    await message.add_reaction('1️⃣')
    await message.add_reaction('2️⃣')
    await message.add_reaction('3️⃣')
    await message.add_reaction('4️⃣')
    await message.add_reaction('5️⃣')
    await message.add_reaction('8️⃣')
    await message.add_reaction('🔟')
    await message.add_reaction('👻')
    await message.add_reaction('🤔')
    await message.add_reaction('🏁')


@client.command(pass_context=True)
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    await ctx.channel.purge(limit=int(amount))
    await channel.send('Messages deleted.')


client.run(DISCORD_TOKEN)

