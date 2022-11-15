import discord
from discord.ext import commands
from features import _available
from features.get_time import *
from features.send_ping import *

##########################################################

TOKEN_FILE = open("./asset/token/token.txt", 'r')
TOKEN      = TOKEN_FILE.readline()
TOKEN_FILE.close()

bot = commands.Bot(command_prefix = 'axl! ', help_command=None, intents=discord.Intents.all())

##########################################################

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')

##########################################################

@bot.command(name = "change_status")
@commands.is_owner()
async def change_status(ctx, *args):
    available_status = {"online" : "온라인",
                        "offline" : "오프라인", 
                        "idle" : "대기", 
                        "do_not_disturb" : "방해금지",
                        "invisible" : "숨김"}
    request = args[0]
    await bot.change_presence(status = getattr(discord.Status, request))
    embed = discord.Embed(title = "상태 전환 성공", 
                        description = f"봇({bot.user})를 성공적으로 **{available_status[request]}({request})** 상태로 전환했습니다.", 
                        color = 0x00FFDB)
    await ctx.reply(embed = embed)

@bot.command(name = "hello")
async def hello(ctx):
    await ctx.reply(f"반가워요! **{ctx.author.name}**님! 저는 **{bot.user}** 입니다!")

@bot.command(name = "help")
async def help(ctx, *args):
    if not args:
        available_commands_list = ""
        for _dataline in _available.supported_commands:
            available_commands_list += f"`{_dataline}` "
        embed = discord.Embed(title = "명령어 도움말", color = 0xE4F9F5)
        embed.add_field(name = "사용 가능한 명령어", value = f"{available_commands_list}", inline = False)
        embed.add_field(name = "공통 명령어 형식(prefix)", value = f"`axl! [command] [args...]`", inline = False)
        embed.add_field(name = "특정 명령어 자세하게 알아보기", value = f"`!help [command]`\n(`[command]`에서 명령어 앞의 axl!는 붙이지 마세요.)", inline = False)
        await ctx.reply(embed = embed)
    elif len(args) == 1:
        request = "!" + args[0]
        if request in _available.supported_commands:
            detailed_guide              = _available.supported_commands[request]
            detailed_guide_description  = detailed_guide["description"]
            detailed_guide_usage        = detailed_guide["usage"]
            detailed_guide_privilege    = detailed_guide["privilege"]
            embed = discord.Embed(title = f"자세한 명령어 도움말 `({request})`", color = 0xE4F9F5)
            embed.add_field(name = "명령어 설명", value = f"{detailed_guide_description}", inline = False)
            embed.add_field(name = "명령어 형식", value = f"`{detailed_guide_usage}`", inline = False)
            embed.add_field(name = "명령어 권한", value = f"`{detailed_guide_privilege}`", inline = False)
            embed.set_footer(text = "명령어 권한이 administrator인 경우 권한이 있는 관리자만 실행할 수 있어요.")
            await ctx.reply(embed = embed)
    else:
        await ctx.reply(f"명령어 형식이 올바르지 않은 것 같아요. (`axl! help [args...]`)")

@bot.command(name = "ping")
async def ping(ctx, *args):
    if not args:
        # no input
        await ctx.reply(f"`ping` 명령어를 위한 제대로 된 인수가 주어지지 않은 것 같아요. (도움말 참조)")
    else:
        ping_result = send_ping(args[0])
        if ping_result == "illegal input for ping":
            # illegal input
            await ctx.reply(f"`ping` 명령어를 위한 인수가 적절하지 않습니다. (도움말 참조)")
        else:
            embed = discord.Embed(title = f"`ping` 보내기", color = 0x00FFDB)
            embed.add_field(name = "목적지", value = f"`{args[0]}`", inline = False)
            embed.add_field(name = "결과", value = f"**{ping_result['message']}** ({ping_result['success_ratio_percentage']}%)", inline = False)
            embed.add_field(name = "RTT", value = f"**평균** : {ping_result['rtt_avg_ms']}ms, **최대** : {ping_result['rtt_max_ms']}ms, **최소** : {ping_result['rtt_min_ms']}ms")
            embed.set_footer(text = "IP주소나 URL로 ping을 시도할 수 있어요.")
            await ctx.reply(embed = embed)

@bot.command(name = "time")
async def get_time(ctx):
    current_time = get_current_formatted_time_string()
    embed = discord.Embed(title = "현재 시간", 
                        description = f"{current_time}", 
                        color = 0x00FFDB)
    embed.set_footer(text = "한국표준시(KST) 기준")
    await ctx.reply(embed = embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        embed = discord.Embed(title = "권한 부족", 
                            description = f"제시하신 명령어 `{ctx.message.content}`는 관리자만 실행할 수 있습니다.", 
                            color = 0xFF0000)
        await ctx.reply(embed = embed)
    else:
        embed = discord.Embed(title = "예외 발생", 
                            description = "명령어가 올바르지 않거나 실행 과정에서 오류가 발생했습니다.", 
                            color = 0xFF0000)
        embed.add_field(name = "에러 로그", value = f"`{error}`", inline = True)
        embed.set_footer(text = "제대로 된 실행에도 오류가 계속되면 관리자에게 연락하세요.")
        await ctx.reply(embed = embed)
    pass

bot.run(TOKEN)