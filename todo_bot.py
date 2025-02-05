#!/usr/bin/python3
from discord.ui import Modal, TextInput
from discord.ext import commands
import discord
import os
import json
from dotenv import load_dotenv
load_dotenv()

def read_todo(group):
    try:
        with open(f"todos/{group}.json", 'r', encoding='utf-8') as file:
            try:
                todo_list = json.load(file)
                return todo_list
            except:
                print("empty file")
                update_todo(group, [])
                return []
    except:
        update_todo(group, [])
        print("no such file")
        return []

def update_todo(group, todo_list):
    with open(f"todos/{group}.json", 'w', encoding='utf-8') as file:
        json.dump(todo_list, file, ensure_ascii=False, indent=4)

# load todo_list
# todo_list = read_todo(message.channel.name)
# if todo_list == None:
#     update_todo(message.channel.name, [])

# class todo:
#     def __init__(self, target:str, done:bool):
#         self["target"] = target
#         self["done"] = done  # True/False

class MyModal(Modal, title="MyModal"):
                            
    # 添加文本输入字段
    name = TextInput(label="你的名字", placeholder="在这里输入你的名字", min_length=2, max_length=100)
    
    async def on_submit(self, interaction:discord.Interaction):
        await interaction.response.send_message(f"your name is {self.name.value}!")

    # 当模态被提交时，这个异步方法将被调用
    #async def callback(self, interaction: discord.Interaction):
    #    # 从模态获取输入值
    #    name = self.children[0].value
    #    # 做一些处理，比如发送消息
    #    await interaction.response.send_message(f"你的名字是：{name}")

class todo_modal(Modal, title="to do or not to do"):
                            
    # 添加文本输入字段
    doit = TextInput(label="what todo?", placeholder="input your todo", max_length=100, required=True)
    
    async def on_submit(self, interaction:discord.Interaction):
        repeated = False
        todo_list = read_todo(interaction.guild.name)
        for t in todo_list:
            if self.doit.value == t["target"]:
                repeat = True
                break
    
        if repeated:
            await interaction.response.send_message("todo: {self.doit.value} is already existed!")
        else:
            todo = {'target':self.doit.value, 'done':'0'}
            todo_list.append( todo )
            update_todo(interaction.guild.name, todo_list)
            print(todo_list)
            await interaction.response.send_message(f"\"**{self.doit.value}**\" to do or not to do")

def print_todo(group):
    todo = read_todo(group)
    for do in todo:
        print(do["target"])

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
description = '''python todo bot'''
# bot 需要甚麼訊息
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', description=description, intents=discord.Intents.all())



@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"Logged in as {bot.user.name} {bot.user.id}")
    print(f"載入 {len(slash)} 個斜線指令")
    for cmd in slash:
        print(cmd.name)
    print("---------")

@bot.tree.command(name="add", description="add a todo")
async def add_todo(interaction:discord.Interaction):
    await interaction.response.send_modal(todo_modal())
    print_todo(interaction.guild.name)

@bot.tree.command(name="del", description="delete a todo forever!")
async def del_todo(interaction:discord.Interaction, *, delete_todo:str):
    # 延遲回覆
    await interaction.response.defer()

    found = False
    finished = True
    todo_list = read_todo(interaction.guild.name)
    for do in todo_list:
        if do["target"] == delete_todo:
            if do["done"] == '1':
                finished = True
            else:
                finished = False
            todo_list.remove(do)
            update_todo(interaction.guild.name, todo_list)
            found = True
            break
    
    if found:
        if finished:
            # await interaction.response.send_message(f"deleted {delete_todo}!!")
            # 因為延遲回覆，所以要用followup
            await interaction.followup.send(f"deleted \"**{delete_todo}**\"")
        else:
            # await interaction.response.send_message(f"deleted {delete_todo}!!")
            await interaction.followup.send(f"deleted \"**{delete_todo}**\"")

    else:
        # nawait interaction.response.send_message("todo not found")
        await interaction.followup.send("todo \"**{delete_todo}**\" not found")
    print_todo(interaction.guild.name)

@bot.tree.command(name="del_all", description="delete a todo forever!")
async def del_all_todo(interaction:discord.Interaction):
    update_todo(interaction.guild.name,[])
    await interaction.response.send_message(f"deleted all!!")
    

@bot.tree.command(name="fin", description="report robot you finished a todo")
async def finish_todo(interaction:discord.Interaction, *, finish_todo:str):
    await interaction.response.defer()

    found = False
    todo_list = read_todo(interaction.guild.name)
    for do in todo_list:
        if do["target"] == finish_todo:
            do["done"] = '1'
            found = True
            update_todo(interaction.guild.name, todo_list)
            break

    if found:
        # await interaction.response.send_message(f"congragulation!! you finished {finish_todo}")
        await interaction.followup.send(f"congragulation!! you finished \"**{finish_todo}**\"")
    else:
        # await interaction.response.send_message("I didn't find it.\nDid you realy finished it?")
        await interaction.followup.send("I didn't find it.\nDid you realy finished it?")
    print_todo(interaction.guild.name)


@bot.tree.command(name="show", description="show todos that we haven't finished")
async def show_todo(interaction:discord.Interaction):
    await interaction.response.defer()

    embed=discord.Embed(
            title="todo list", 
            url="https://youtu.be/vKB2Lg-IM3I?si=dYAN7DoXXMAY2pSp",
            # description="dodo 大神肯定可以自己完成對吧",   
            color=discord.Color.blue()
    )
    # embed.set_image(url="http://photo.kubar.cn/photo/21374/20210722/20210722_1626921091_4927_4615_8651_8751.jpg")
    # embed.set_footer(text="to do or not to do")
    all_done = True
    todo_list = read_todo(interaction.guild.name)
    if todo_list:
        for do in todo_list:
            if do["done"] == '0':
                all_done = False
                embed.add_field(name=f"[X] {do['target']}", value="", inline=False)
    if all_done:
        embed.add_field(name="no todo need to do!!", value="", inline=False)

    # await interaction.response.send_message(embed = embed)
    await interaction.followup.send(embed = embed)
    print_todo(interaction.guild.name)

@bot.tree.command(name="show_all", description="show all todos")
async def show_all_todo(interaction:discord.Interaction):
    await interaction.response.defer()

    embed=discord.Embed(
            title="todo list", 
            url="https://youtu.be/vKB2Lg-IM3I?si=dYAN7DoXXMAY2pSp", 
            # description="dodo 大神肯定可以自己完成對吧", 
            color=discord.Color.blue()
    )
    # embed.set_image(url="http://photo.kubar.cn/photo/21374/20210722/20210722_1626921091_4927_4615_8651_8751.jpg")
    # embed.set_footer(text="to do or not to do")
    todo_list = read_todo(interaction.guild.name)
    if todo_list:
        # print(todo_list)
        for do in todo_list:
            if do["done"] == '0':
                embed.add_field(name=f"[X] {do['target']}", value="", inline=False)
        for do in todo_list:
            if do["done"] == '1':
                embed.add_field(name=f"[O] {do['target']}", value="", inline=False)

    else:
        embed.add_field(name="no todo need to do!!", value="", inline=False)

    # print(len(todo))
    # await interaction.response.send_message(embed = embed)
    await interaction.followup.send(embed = embed)
    print_todo(interaction.guild.name)

@bot.tree.command(name="help", description="explan all commands")
async def help(interaction: discord.Interaction,):
    await interaction.response.send_message("""
/add: add a todo
/del: delete a todo
/del_all: delete all todos
/fin: finish a todo
/show: show unfinished todos
/show_all: show all todos
/hello: test todo bot 
""")


@bot.tree.command(description="say hello")
async def hello(interaction: discord.Interaction, *, name:str):
    #print(f"{ctx.author} say something\nin sever: {ctx.guild}\nin channel: {ctx.channel}")
    print(f"hello {name} in {interaction.guild.name}!!")
    await interaction.response.send_message(f"hello {name}!!")
    # embed = discord.Embed(title="标题", description="这是嵌入消息的描述", color=0x00ff00)
    # await ctx.send(embed=embed)


# @bot.command()
# async def embed_demo(ctx):
#     # 创建 Embed 对象
#     embed = discord.Embed(
#         title="示例标题",  # Embed 的标题
#         description="这里是描述文本",  # Embed 中的描述文字
#         color=discord.Color.blue()  # Embed 边框颜色
#     )

#     # 添加字段（可选）
#     embed.add_field(name="字段 1", value="这是字段 1 的值", inline=False)
#     embed.add_field(name="字段 2", value="这是字段 2 的值", inline=True)
#     embed.add_field(name="字段 3", value="这是字段 3 的值", inline=True)

#     # 设置脚注（可选）
#     embed.set_footer(text="这是脚注文本")

#     # 设置缩略图（可选）
#     embed.set_thumbnail(url="https://toppng.com/uploads/preview/discord-logo-discord-ico-11562851206m28xz1b1ln.png")

#     # 设置作者信息（可选）
#     embed.set_author(name="作者名", icon_url="https://static.vecteezy.com/system/resources/previews/000/550/731/original/user-icon-vector.jpg")

#     # 设置图片（可选）
#     embed.set_image(url="https://toppng.com/uploads/preview/discord-logo-discord-ico-11562851206m28xz1b1ln.png")
    
#     # 发送 Embed 消息
#     await ctx.send(embed=embed)

# @bot.tree.command(name="modal_demo", description="maybe just for testing?")
# async def modal_demo(interaction: discord.Interaction):
#     # 创建模态实例
#     modal = MyModal()
#     # 显示模态给用户
#     await interaction.response.send_modal(todo_modal())



bot.run(TOKEN)
