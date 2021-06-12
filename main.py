import discord
from discord.ext import commands
import time
from asyncio import sleep
import random
import json
import sqlite3
from discord.ext import tasks
import traceback
import datetime
client = commands.Bot(command_prefix = ".",intents = discord.Intents.all())
client.remove_command("help")
connection = sqlite3.connect('iponergoodestman.iponer')
cursor = connection.cursor()
@client.event
async def on_ready():
    print('Bot is ready')
    print('Users: ' + str(len(client.users)))
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            id INT,
            server_id INT,
            cash BIGINT CHECK (cash >= 0),
            voice BIGINT,
            lvl BIGINT,
            messages BIGINT,
            warn BIGINT
          )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
            role_id INT,
            id INT,
            cost BIGINT
        )""")


    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(F"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute("INSERT INTO users VALUES (?,?,?,0,0,0,0,0)", (member.name, member.id, member.guild.id))
                connection.commit() #bd
            else:
                pass
        connection.commit()

@client.event
async def on_member_join(member):
    if cursor.execute(F"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute("INSERT INTO users VALUES (? ,?, ?,0,0,0,0,0)", (member.name,member.id, member.guild.id))
        connection.commit() #bd
    else:
        pass
    channel = client.get_channel(728693828701388803)
    embed = discord.Embed(
        colour=discord.Colour.from_rgb(47, 49, 54),
        title="Добро пожаловать",
        description="Приветитсвую вас на нашем сервере!Не забывай смотреть правила"
    )
    await channel.send(f"{member.mention}",embed=embed)




@client.command()
async def buy(ctx,role: discord.Role=None):
    if role is None:
        await ctx.send("{ctx.author} укажите роль,которую хотите купить")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author}**,у вас имеется данная роль")
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author},У вас недостаточно средств для покупки этой роли!**")
        else:
            await ctx.author.add_role(role)
            cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0],ctx.author.id))
            await ctx.send(f"**{ctx.author.id}**,Роль успешна куплена")


@client.command()
async def add_shop(ctx, role: discord.Role=None,cost : int=None):
    if role is None:
        await ctx.send(f"**{ctx.author},укажите роль,которые вы желаете внести в магазин**")
    else:
        if cost is None:
            await ctx.send(f"**{ctx.author}** укажите стоимость данной роли")
        elif cost < 0:
            await ctx.send(f"**{ctx.author}, стоимость роли не может быть такой маленькой**")
        else:
            await ctx.send("Роль успешно добавлена")
            cursor.execute("INSERT INTO shop VALUES ({},{},{})".format(role.id, ctx.guild.id, cost))
            connection.commit()





@client.command()
async def remove_shop(ctx,role:discord.Role=None):
    if role is None:
        await ctx.send(f"{ctx.author},укажите роль,которую вы хотите удалить из магазина")
    else:
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
        connection.commit()

        await ctx.send("Роль успешна удалена из магазина")

@client.command()
async def shoprole(ctx):
    embed = discord.Embed(title= 'Магазин ролей')

    for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed = discord.Embed(
            title = 'Shop',
            colour = discord.Colour.from_rgb(153, 204, 255)
            )
            embed.add_field(
                name = f"Стоимость **{row[1]}**",
                value = f"Вы приобретаете роль {ctx.guild.get_role(row[0]).mention}"
            )

            await ctx.send(embed=embed)
        else:
            pass



@client.command()
async def delite(ctx):
    cursor.execute("UPDATE users SET voice = 0")
    connection.commit()
    await ctx.send("Успешно")

@client.event
async def on_voice_state_update(member, before, after):
    global current_date_time
    if before.channel is None and after.channel is not None:
        current_date_time = datetime.datetime.now()
    if before.channel and not after.channel:
        current_time = current_date_time.now()
        fultime = current_time - current_date_time
        fultime = fultime.total_seconds()
        sec = round(fultime)
        sec_value = sec % (24 * 3600)
        hour_value = sec_value // 3600
        sec_value %= 3600
        min_value = sec_value // 60
        sec_value %= 60
        #await member.guild.system_channel.send(f"""{round(hour_value)} часов,{round(min_value)}минут, {round(sec_value)} секунд""")
        cursor.execute("UPDATE users SET voice = voice + ? WHERE id = ?", (sec, member.id,))
        connection.commit()
@client.command()
async def profile(ctx):
    messageprint = cursor.execute("SELECT messages FROM users WHERE id = ?", (ctx.author.id,)).fetchone()[0]
    voiceprint = cursor.execute("SELECT voice FROM users WHERE id = ?", (ctx.author.id,)).fetchone()[0]
    warnprint = cursor.execute("SELECT warn FROM users WHERE id = ?", (ctx.author.id,)).fetchone()[0]
    lvlprint = cursor.execute("SELECT lvl FROM users WHERE id = ?", (ctx.author.id,)).fetchone()[0]
    economyprint = cursor.execute("SELECT cash FROM users WHERE id = ?", (ctx.author.id,)).fetchone()[0]
    sec = voiceprint
    sec_value = sec % (24 * 3600)
    hour_value = sec_value // 3600
    sec_value %= 3600
    min_value = sec_value // 60
    sec_value %= 60
    embed = discord.Embed(
        colour=discord.Colour.from_rgb(47, 49, 54),
        title="Профиль",
        description="Мой прекрасный профиль..."
    )
    embed.add_field(name="Валюта", value=f"**{economyprint}** :crown:", inline=False)
    embed.add_field(name="Всего соабщений",value=f"**{messageprint}**",inline=True)
    #embed.add_field(name="Уровни", value=f"**{lvlprint}**", inline=True)
    embed.add_field(name="Варны", value=f"**{warnprint}**", inline=True)
    embed.add_field(name="Голосовой актив", value=f"**{round(hour_value)}** часов ,**{round(min_value)}** минут, **{round(sec_value)}** секунд", inline=False)
    await ctx.send(embed=embed)
@client.command()
async def casino(ctx,moneys=None,member: discord.Member = None):
  b = ['1','2']
  a = random.choice(b)
  if moneys is None:
    await ctx.send("Укажите сумму ставки")
  if a == "1":
    try:
        cursor.execute("UPDATE users SET cash = cash -" + str(moneys) + " WHERE id = {}".format(ctx.author.id))
        moneys = int(moneys)
        connection.commit()
        await ctx.send(f"""
    Вы проиграли: {moneys} :crown:
Ваш баланс: **{ctx.author}** составляет  **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} ** :crown:
    """)
    except:
        await ctx.send(f"{ctx.author},у вас нехватает денег")
  if a == "2":
    try:
        cursor.execute("UPDATE users SET cash = cash -" + str(moneys) + " WHERE id = {}".format(ctx.author.id))
        moneys = int(moneys) * 2
        cursor.execute("UPDATE users SET cash = cash +" + str(moneys) +" WHERE id = {}".format(ctx.author.id))
        connection.commit()
        await ctx.send(f"""
    Вы выйграли: {moneys} :crown:
Ваш баланс: **{ctx.author}** составляет  **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} ** :crown:
    """)
    except:
        await ctx.send(f"{ctx.author},у вас нехватает денег")
@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (50, ctx.author.id,))
    connection.commit()
    await ctx.send(f"{ctx.author},Вы получили 50 монет")
@client.command()
@commands.has_guild_permissions()
async def give(ctx,members:discord.Member=None,moneysa=None):
    cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (moneysa, members.id,))
    connection.commit()
    await ctx.send(f"успешно.")
@client.command()
async def leaderboardvoice(ctx):
    embed = discord.Embed(title='топ 10 сервера по часам войса')
    counter = 0
    for row in cursor.execute("SELECT name, voice From users WHERE server_id = {} ORDER BY cash DESC LIMIT 10".format(ctx.guild.id)):
        counter += 1
        embed.add_field(name=F'# {counter} | {row[0]} ', value=F'Баланс: {row[1]}', inline=False)
    await ctx.send(embed=embed)
@client.command()
async def leaderboardeconomy(ctx):
    embed = discord.Embed(title='топ 10 сервера по валюте')
    counter = 0
    for row in cursor.execute("SELECT name, cash From users WHERE server_id = {} ORDER BY cash DESC LIMIT 10".format(ctx.guild.id)):
        counter += 1
        embed.add_field(name=F'# {counter} | {row[0]} ', value=F'Баланс: {row[1]}', inline=False)
    await ctx.send(embed=embed)
@client.command()
async def balance(ctx, members: discord.Member = None):
  if members is None:
        embed = discord.Embed(
        title = f"{ctx.author}",
        colour=discord.Colour.from_rgb(47, 49, 54),
        )
        embed.add_field(name=f"""Баланс пользователя составляет {cursor.execute("SELECT cash FROM users WHERE id = ?", (ctx.author.id,)).fetchone()[0]} :candy: """,value=f"_ _",inline=False)
        await ctx.send(embed=embed)
  else:
      embed = discord.Embed(
          title = f"{members}",
          colour=discord.Colour.from_rgb(47, 49, 54),
      )
      embed.add_field(name=f"""Баланс пользователя составляет {cursor.execute("SELECT cash FROM users WHERE id = ?", (members.id,)).fetchone()[0]} :candy: """,value=f"_ _", inline=False)
      await ctx.send(embed=embed)
@client.event
async def on_message(message):
    await client.process_commands(message)
    cursor.execute("UPDATE users SET messages = messages + ? WHERE id = ?", (1, message.author.id,))
    connection.commit()
@client.command()
async def send(ctx,gif="nos",*,slova=None):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send('У вас не хватает прав!')
    if ctx.message.author.guild_permissions.administrator:
        if slova is None:
            await ctx.send(f"{ctx.author},Вы не указали слова для отправления")
        else:
            await ctx.message.delete()
            embed = discord.Embed(
                colour=discord.Colour.from_rgb(47, 49, 54),
                description=slova
            )
            if gif == "no":
                await ctx.send(embed=embed)
            if not gif == "no":
                embed.set_image(url=gif)
                await ctx.send(embed=embed)
@client.listen("on_command_error")
async def cooldown_message(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
        title = 'Cooldown:',
        colour = discord.Colour.from_rgb(255, 20, 20)
        )
        embed.add_field(name="Error", value=f"комманду {ctx.command.qualified_name} можно использовать только {error.cooldown.rate} раз в {error.cooldown.per} секунд. Попробуйте через {error.retry_after:.0f} секунд.", inline=False)
        await ctx.send(embed=embed)
    else:
        raise error

@client.command()
async def help(ctx):
    embed = discord.Embed(
        colour=discord.Colour.from_rgb(47, 49, 54),
        title=f"{ctx.author} Мой список комманд",
        description="Некоторые комманды работают только для администрации"
    )
    embed.add_field(name="сasino {ставка}",value="<:1382_dot:852864880243245097> Ставка валюты вы можете проиграть или выйграть.",inline=False)
    embed.add_field(name="balance {участник}",value="<:1382_dot:852864880243245097> Узнать свой баланс или игрока.",inline=False)
    embed.add_field(name="daily", value="<:1382_dot:852864880243245097> Вы можете каждый день получать 50 монет.", inline=False)
    embed.add_field(name="profile", value="<:1382_dot:852864880243245097> Посмотреть свой профиль.",inline=False)
    embed.add_field(name="give {участник}", value="<:1382_dot:852864880243245097> Выдать человеку баланс.Ps тока для администрации.",inline=False)
    embed.add_field(name="leaderboardeconomy", value="<:1382_dot:852864880243245097> Посмотреть топ по экономике.", inline=False)
    embed.add_field(name="leaderboardvoice", value="<:1382_dot:852864880243245097> Посмотреть топ по часам в войсе.",inline=False)
    await ctx.send(embed=embed)


@client.command(aleases=["пощёчина"])
async def пощёчина(ctx, member: discord.Member = None):
    embed = discord.Embed(
        title='Реакции',
        colour=discord.Colour.from_rgb(153, 204, 255),
        description=f"{ctx.author.mention} дает пощечину {member.mention}"
    )
    url = ['https://media1.tenor.com/images/299366efafc95bc46bfd2f9c9a46541a/tenor.gif?itemid=16819981',
           'https://i.pinimg.com/originals/68/de/67/68de679cc20000570e8a7d9ed9218cd3.gif',
           'https://thumbs.gfycat.com/BabyishBeneficialDoe-size_restricted.gif',
           'https://i.pinimg.com/originals/c6/00/12/c60012a00fd5257d71d734f57910bf33.gif']
    url = (random.choice(url))
    embed.set_image(url=url)

    await ctx.send(embed=embed)


@client.command()
async def дать(ctx,xuy=None,member: discord.Member = None):
    if xuy == "пять":
        if member == ctx.author:
            await ctx.send("Вы не можете сделать реакцию с самим собой")
        else:
            embed = discord.Embed(
                title='Реакции',
                colour=discord.Colour.from_rgb(153, 204, 255),
                description=f"{ctx.author.mention} дает пять {member.mention}"
            )
            url = [
                'http://pa1.narvii.com/6384/7bc7fa9e1776f1d9c37f694179bdda1863ac6073_00.gif',
                'http://pa1.narvii.com/5966/80277115ddededfe4fb0b8e274ed0c52db0c0949_hq.gif',
                'https://thumbs.gfycat.com/ActualWarmheartedDungbeetle-size_restricted.gif',
                'https://pa1.narvii.com/6400/0c90019e56cf232a9cc4a73ee368ffbb101b6a3f_hq.gif'
            ]
            url = (random.choice(url))
            embed.set_image(url=url)
            await ctx.send(embed=embed)
@client.command()
async def укусить(ctx,member: discord.Member = None):
    if member == ctx.author:
        await ctx.send("Вы не можете сделать реакцию с самим собой")
    else:
        embed = discord.Embed(
            title='Реакции',
            colour=discord.Colour.from_rgb(153, 204, 255),
            description = f"{ctx.author.mention} лижет {member.mention}"
        )
        url = [
            'https://pa1.narvii.com/6687/26eaef4b158aab82e6a4c4ba91693da496372016_hq.gif',
            'https://pa1.narvii.com/6780/2c9688d787905d0006c256ed8f94249fbfb2d95c_hq.gif',
            'https://i.pinimg.com/originals/e8/f0/40/e8f04097f001ed4a45dba2ebbbe6bbc0.gif'
            ]
        url = (random.choice(url))
        embed.set_image(url=url)
        await ctx.send(embed=embed)

@client.command(aleases=["обнять"])
async def обнять(ctx, member: discord.Member = None):
    if member == ctx.author:
        await ctx.send("Вы не можете сделать реакцию с самим собой")
    else:
        embed = discord.Embed(
        title='Реакции',
        colour=discord.Colour.from_rgb(153, 204, 255),
        description=f"{ctx.author.mention} обнимает {member.mention}"
        )
        url = ['https://acegif.com/wp-content/gif/anime-hug-12.gif',
               'https://giffiles.alphacoders.com/201/201915.gif',
               'https://i.pinimg.com/originals/9e/37/86/9e378638db8cc4d64f54e8bb9e924c3e.gif',
               'https://pa1.narvii.com/6765/b082a857da92e16def6d429fcbfc2cd529799201_hq.gif',
               'https://data.whicdn.com/images/233559365/original.gif',
               'https://pa1.narvii.com/6765/b082a857da92e16def6d429fcbfc2cd529799201_hq.gif',
               'https://pa1.narvii.com/6503/4d18935416c0aff9141b5d712c91f415d3f37a8b_hq.gif',
               'https://data.whicdn.com/images/218924967/original.gif',
               'https://data.whicdn.com/images/98781828/original.gif',
               'https://i.pinimg.com/originals/32/89/d8/3289d80dcec9c95a0b895a479b90e88c.gif',  # 10
               'https://acegif.com/wp-content/gif/anime-hug-1.gif',
               'https://www.anime-graffiti.com/wp-content/uploads/img/201504/20150427-k102.gif',
               'https://pa1.narvii.com/6998/4f34261cb5c67c599cce8166e5396507c7a3cd5dr1-540-304_hq.gif',
               'https://otvet.imgsmail.ru/download/d12cee7ab1dae323435d4dae35178907_i-913.gif',
               'https://acegif.com/wp-content/gif/anime-hug-49.gif',
               'https://i.pinimg.com/originals/cb/4d/69/cb4d691799c3cb2b2e7be0e13b2ac183.gif',
               'https://i.pinimg.com/originals/ea/e1/54/eae154c1c30cc252035e5648f29bf2a1.gif',
               'https://giffiles.alphacoders.com/757/75748.gif',
               'https://data.whicdn.com/images/87333686/original.gif',
               'https://data.whicdn.com/images/236902451/original.gif',  # 20
               'https://im0-tub-ru.yandex.net/i?id=4f6638de4165f0d92aab023ababd43ef&n=13',
               'https://i.pinimg.com/originals/64/c4/6e/64c46e7b7e45748c2e0d2bb992961299.gif',
               'https://i.pinimg.com/originals/5b/83/7c/5b837c1c170d8bf77d11cbdca09eb8eb.gif',
               'https://pa1.narvii.com/6765/b082a857da92e16def6d429fcbfc2cd529799201_hq.gif',
               'https://i.pinimg.com/originals/6b/4b/b8/6b4bb8820a05a841d3317172b7b0224f.gif']  # 25
        url = (random.choice(url))
        embed.set_image(url=url)

        await ctx.send(embed=embed)


@client.command(aleases=["поцелуй", "целовать", "поцеловать"])
async def поцеловать(ctx, member: discord.Member = None):
    if member == ctx.author:
        await ctx.send("Вы не можете сделать реакцию с самим собой")
    else:
        embed = discord.Embed(
        title='Реакции',
        colour=discord.Colour.from_rgb(153, 204, 255),
        description=f"{ctx.author.mention} целует {member.mention}"
        )
        url = ['https://i.pinimg.com/originals/78/10/a0/7810a059eb4b9431b9bb7633f3454338.gif',
               'https://i.imgur.com/So3TIVK.gif',
               'https://animesher.com/orig/0/79/793/7930/animesher.com_boy-feels-shoujo-793037.gif',
               'https://lh3.googleusercontent.com/proxy/d07okqbedXs1Ae13nhCYxIPfo13_98qubAkBRerLLYRFaNAQ-BAtAqeZUPMacOQHHe49j8NN7PB_rqQVgfJ5gJDA_B0UBRfMeFGhjtW7wABEEkqDeaytoNjXlFU',
               'https://cdn.myanimelist.net/s/common/uploaded_files/1483589844-8d0395a7386d12026399620c087f4b97.gif',
               'https://i2.wp.com/nileease.com/wp-content/uploads/2020/12/01ecec4d49676c0a531bf76380561f20.gif?fit=500%2C281&ssl=1',
               'http://37.media.tumblr.com/7bbfd33feb6d790bb656779a05ee99da/tumblr_mtigwpZmhh1si4l9vo1_500.gif'
               'https://cutewallpaper.org/21/romance-anime-with-kissing/Anime-Kissing-GIF-Anime-Kissing-Kiss-Discover-and-Share-GIFs.gif',
               'https://i1.wp.com/nileease.com/wp-content/uploads/2021/03/0939ae60d616a4c7265da52e4abd0089.gif?fit=498%2C284&ssl=1',
               'https://media1.giphy.com/media/nyGFcsP0kAobm/giphy.gif',
               'https://i.imgur.com/0WWWvat.gif',
               'https://data.whicdn.com/images/160215214/original.gif',
               'https://i1.wp.com/loveisaname.com/wp-content/uploads/2016/09/23.gif',
               'https://acegif.com/wp-content/uploads/anime-kissin-8.gif',
               'https://i.imgur.com/OE7lSSY.gif']
        url = (random.choice(url))
        embed.set_image(url=url)
        await ctx.send(embed=embed)


@client.command(aleases=["лизнуть"])
async def лизнуть(ctx,member: discord.Member = None):
    if member == ctx.author:
        await ctx.send("Вы не можете сделать реакцию с самим собой")
    else:
        embed = discord.Embed(
        title='Реакции',
        colour=discord.Colour.from_rgb(153, 204, 255),
        description = f"{ctx.author.mention} лижет {member.mention}"
        )
        url = [
        'https://pa1.narvii.com/7101/224b3367affb1ed0dcbead814f3f4ebf89b35a54r1-542-307_hq.gif',
        'https://pa1.narvii.com/7227/36c554aa3bc6b52963f134cf48dfb06422a7367dr1-896-504_hq.gif'
        ]
        url = (random.choice(url))
        embed.set_image(url=url)
        await ctx.send(embed=embed)

@client.command()
async def ударить(ctx,member: discord.Member = None):
    if member == ctx.author:
        await ctx.send("Вы не можете сделать реакцию с самим собой")
    else:
        embed = discord.Embed(
            title='Реакции',
            colour=discord.Colour.from_rgb(153, 204, 255),
            description = f"{ctx.author.mention} ударяет {member.mention}"
        )
        url = ['https://pa1.narvii.com/7194/bb26d1c8a9a978dd6c50b91ffca471d7036b55f4r1-560-315_hq.gif',
        'https://media1.tenor.com/images/299366efafc95bc46bfd2f9c9a46541a/tenor.gif?itemid=16819981',
        'https://media1.tenor.com/images/a0ff9e6e3f65b921d63dfffeec0b94a0/tenor.gif?itemid=7202047',
        'https://pa1.narvii.com/7666/f37253bf56f2a1fbbe984e0ff53ed4138519f849r1-500-281_hq.gif'

        ]
        url = (random.choice(url))
        embed.set_image(url=url)
        await ctx.send(embed=embed)
@client.command()
async def погладить(ctx,member: discord.Member = None):
    if member == ctx.author:
        await ctx.send("Вы не можете сделать реакцию с самим собой")
    else:
        embed = discord.Embed(
            title='Реакции',
            colour=discord.Colour.from_rgb(153, 204, 255),
            description = f"{ctx.author.mention} гладит {member.mention}"
        )
        url = [
            'https://pa1.narvii.com/6607/1f16bfa7ba7763602c172cfef17510ec863872a0_hq.gif',
            'https://thumbs.gfycat.com/TautInformalIndianjackal-small.gif',
            'https://data.whicdn.com/images/258779638/original.gif'

        ]
        url = (random.choice(url))
        embed.set_image(url=url)
        await ctx.send(embed=embed)

@client.command()
async def плакать(ctx):
    embed = discord.Embed(
        title='Реакции',
        colour=discord.Colour.from_rgb(153, 204, 255),
        description = f"{ctx.author.mention} плачет"
    )
    url = [
        'https://2ch.pm/dr/src/404128/16004095673900.gif',
        'https://data.whicdn.com/images/225223315/original.gif',
        'https://pa1.narvii.com/6827/e839e40326ece5a98e92e21981ce44cbb0cedcb1_hq.gif'

    ]
    url = (random.choice(url))
    embed.set_image(url=url)
    await ctx.send(embed=embed)



client.run("TOKEN")
