import requests
import time
import random
import os
import ast
import pickle
import discord
from ..convert_number_notation import get_korean_number_amount

class CustomUserAgentString:

    user_agent_string_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Mozilla/5.0 (Windows NT 10.0; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35'
    ]

class get_kr_finance_information:

    @staticmethod
    def fetch_overall_information():

        # to prevent excessive requests, store data as a JSON file that is valid for 60 seconds
        # kr_finance_raw_data_file_path = f"{os.getcwd()}/kr_index_raw.data.pickle"
        kr_finance_raw_data_file_path = f"./features/finance/indexes/kr_index_raw.data.pickle"

        if not os.path.isfile(kr_finance_raw_data_file_path) or not time.time() - os.path.getmtime(kr_finance_raw_data_file_path) < 60:
        
            request_url_list = { "overview"         : "https://api.finance.naver.com/service/mainSummary.naver",                                      # overview market
                                 "major_indexes"    : "https://polling.finance.naver.com/api/realtime?query=SERVICE_INDEX:KOSPI,KOSDAQ,KPI200" }      # major index
            headers = { "user-agent" : random.choice(CustomUserAgentString.user_agent_string_list) }

            kr_finance_raw_data = {}

            # annotation, url
            for key, value in request_url_list.items():
                response = requests.get(value, headers = headers)
                                                # Python uses "None" instead of "null"
                data = response.text.replace("null", "None")
                kr_finance_raw_data[key] = data

            with open(kr_finance_raw_data_file_path, 'wb') as file:
                pickle.dump(kr_finance_raw_data, file)
        

        with open(kr_finance_raw_data_file_path, 'rb') as file:
            kr_finance_data = pickle.load(file)

        return kr_finance_data


    @staticmethod
    def extract_data_by_criteria(criteria:str):

        kr_finance_data = get_kr_finance_information.fetch_overall_information()

        available_criterias = {
            # daily overall top ranking
            "top_trades"        : ["overview", "message", "result", "topItems", 0],
            "top_rise"          : ["overview", "message", "result", "topItems", 1],
            "top_fall"          : ["overview", "message", "result", "topItems", 2],
            "top_market_cap"    : ["overview", "message", "result", "topItems", 3],
            
            # daily specified ranking
            "group_top_list"    : ["overview", "message", "result", "groupTopList"],
            "theme_top_list"    : ["overview", "message", "result", "themeTopList"],

            # index ranking
            "daily_index_trend" : ["overview", "message", "result", "todayIndexDealTrendList"],     # buy/sell trend
            "daily_index_items" : ["overview", "message", "result", "todayIndexItemList"],          # rise/even/steady count in the index

            # index value
            "daily_index_stats" : ["major_indexes", "result", "areas"]                              # index stat with highly-abbreviated keys

        }

        if criteria not in available_criterias:
            print("Unavilable criteria")
            return

        # find multi-depth dictionary dynamically according to the given criteria
        result = kr_finance_data

        for search_option in available_criterias[criteria]:
            try:
                result = result[search_option]
            except TypeError:
                result = dict(ast.literal_eval(result))
                result = result[search_option]

        return result


    @staticmethod
    def get_index_overview(index:str):

        if index not in ["KOSPI", "KOSDAQ", "KPI200"]:
            print("Unavailable index")
            return
        
        daily_index_trend   = get_kr_finance_information.extract_data_by_criteria(criteria = "daily_index_trend")
        daily_index_items   = get_kr_finance_information.extract_data_by_criteria(criteria = "daily_index_items")
        daily_index_stats   = get_kr_finance_information.extract_data_by_criteria(criteria = "daily_index_stats")

        if index == "KOSPI":
            data_dict_index = 0
        elif index == "KOSDAQ":
            data_dict_index = 1
        else:       # KPI200
            data_dict_index = 2


        result = {
            "item_code"             : index,

            # index trends (unit : KRW)
            "personal_value"        : round(float(daily_index_trend[data_dict_index]["personalValue"]) * 100000000),
            "foreign_value"         : round(float(daily_index_trend[data_dict_index]["foreignValue"]) * 100000000),
            "institution_value"     : round(float(daily_index_trend[data_dict_index]["institutionalValue"]) * 100000000),

            # index statistics
            "market_open_close"     : daily_index_stats[0]["datas"][data_dict_index]["ms"],
            "current_value"         : int(daily_index_stats[0]["datas"][data_dict_index]["nv"]) / 100,
            "current_change_value"  : int(daily_index_stats[0]["datas"][data_dict_index]["cv"]) / 100,
            "current_change_rate"   : round(daily_index_stats[0]["datas"][data_dict_index]["cr"], 2),       # change rate (%)
            "daily_high_value"      : int(daily_index_stats[0]["datas"][data_dict_index]["hv"]) / 100,
            "daily_low_value"       : int(daily_index_stats[0]["datas"][data_dict_index]["lv"]) / 100,
            "acc_trading_volume"    : int(daily_index_stats[0]["datas"][data_dict_index]["aq"]) * 1000,
            "acc_trading_price"     : int(daily_index_stats[0]["datas"][data_dict_index]["aa"]) * 1000000,  # 1 = million won,
            "graph_image_url"      : f"https://ssl.pstatic.net/imgfinance/chart/main/{index}.png?sidcode={time.time() * 1000}"  # live chart
        }

        if index in ["KOSPI", "KOSDAQ"]:
            # They're not provided in case of KPI200 index overview.
            result.setdefault("upper_limit_count", daily_index_items[data_dict_index]["upperCnt"])
            result.setdefault("rise_count", daily_index_items[data_dict_index]["riseCnt"])
            result.setdefault("steady_count", daily_index_items[data_dict_index]["steadyCnt"])
            result.setdefault("fall_count", daily_index_items[data_dict_index]["fallCnt"])
            result.setdefault("lower_count", daily_index_items[data_dict_index]["lowerCnt"])

        return result

async def show_index_statistics(index_name:str):

    result = get_kr_finance_information.get_index_overview(index = index_name)

    embed = discord.Embed(title = f"{index_name}", color = 0x03C75A)
    embed.add_field(name = "?????? ??????", value = f"`{result['market_open_close']}`", inline = True)
    embed.add_field(name = "?????????", value = f"**{result['current_value']}**", inline = True)
    embed.add_field(name = "??????", value = f"{result['current_change_value']} ({result['current_change_rate']} %)", inline = True)
    embed.add_field(name = "?????? / ??????", value = f"> ?????? ?????? : {result['daily_high_value']}\n> ?????? ?????? : {result['daily_low_value']}", inline = True)
    embed.add_field(name = "1??? ?????? ??????", value = f"> ?????? ?????? : {get_korean_number_amount(result['acc_trading_price'])} ???\n> ????????? ??? {get_korean_number_amount(result['acc_trading_volume'])} ???", inline = False)
    embed.add_field(name = "???????????? ?????? ??????", value = f"> ?????? : {get_korean_number_amount(result['personal_value'])} ???\n> ?????? : {get_korean_number_amount(result['institution_value'])} ???\n> ????????? : {get_korean_number_amount(result['foreign_value'])} ???", inline = True)

    if index_name != "KPI200":
        embed.add_field(name = "?????? ??????", value = f"??? ?? {result['upper_limit_count']} | ???? ?? {result['rise_count']} | ??? ?? {result['steady_count']} | ???? ?? {result['fall_count']} ??? ?? {result['lower_count']}", inline = False)

    embed.set_image(url = result['graph_image_url'])
    embed.set_footer(text = "????????? ????????? ???????????? ????????? ???????????? ????????? ?????? 1????????? ????????? ?????? ?????? ??? ?????????, ?????? ????????? ????????? ?????? ?????? ?????? ?????? ????????? ???????????? ???????????????. ?????? ?????? ???????????? ?????? ???????????? ??????(??? ????????? ??? ????????????)?????? ????????? ????????????. ????????? ????????? KPI200 Index??? ?????? ?????? ????????? ??????????????? ??? ???????????? ?????? ????????????. ????????? ???????????? ????????? ???????????? ?????? ????????? ?????? ????????? ???????????????.")

    return embed


class IndexInfoMenu(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout = 60)
        self.value = None
        self.ctx = ctx

    @discord.ui.button(label = "KOSPI", style = discord.ButtonStyle.grey)
    async def KOSPI(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await show_index_statistics(index_name ="KOSPI")
        await interaction.response.edit_message(embed = embed)

    @discord.ui.button(label = "KOSDAQ", style = discord.ButtonStyle.grey)
    async def KOSDAQ(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await show_index_statistics(index_name ="KOSDAQ")
        await interaction.response.edit_message(embed = embed)

    @discord.ui.button(label = "KPI200", style = discord.ButtonStyle.grey)
    async def KPI200(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await show_index_statistics(index_name ="KPI200")
        await interaction.response.edit_message(embed = embed)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
            
        await self.message.edit(view = self)
        await self.ctx.send("_1??? ?????? ????????? ????????? ?????? ???????????? ???????????????._")