import aiohttp
import lxml.html
import typing as T
from re import findall
from random import choice

from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11.helpers import extract_image_urls, Cooldown

from ATRI.config import SauceNAO
from .data_source import SaouceNao


_search_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])


saucenao = SaouceNao().on_command("以图搜图", "透过一张图搜索可能的来源")


@saucenao.got("saucenao_img", "图呢？", [Cooldown(5, prompt=_search_flmt_notice)])
async def _deal_search(event: MessageEvent):
    user_id = event.get_user_id()
    img = extract_image_urls(event.message)
    if not img:
        await saucenao.reject("请发送图片而不是其他东西！！")

    #try:
    #    a = SaouceNao(SauceNAO.key)
    #except Exception:
    #    await saucenao.finish("失败了...")

    result = f"> {MessageSegment.at(user_id)}" + await do_search(img[0])  # type: ignore
    await saucenao.finish(Message(result))

async def do_search(url: str):
    # saucenao
    s_url = f'https://saucenao.com/search.php?url={url}'

    s_info = await get_saucenao_detail(s_url)

    if s_info and percent_to_int(s_info[0]['Similarity']) > 0.6:
        msg = ''
        for k, v in s_info[0].items():
            if k != 'Content':
                msg += f'{k}: {v}\n'
            else:
                msg += f'{v}\n'
        return msg.strip()
    else:
        msg = '未找到相似图片\n'
        return msg.strip()


async def get_saucenao_detail(s_url):
    async with aiohttp.client.request('GET', s_url) as resp:
        text = await resp.text(encoding='utf8')

    html_e: lxml.html.HtmlElement = lxml.html.fromstring(text)
    results = [
        {
            'Similarity': ''.join(
                r.xpath('.//div[@class="resultsimilarityinfo"]/text()')),
            'Title': ''.join(
                r.xpath('.//div[@class="resulttitle"]/descendant-or-self::text()')),
            'Content': '\n'.join(
                r.xpath('.//div[@class="resultcontentcolumn"]/descendant-or-self::text()')).replace(': \n', ': '),
            'URL': ''.join(
                r.xpath('.//div[@class="resultcontentcolumn"]/a[1]/attribute::href')),
        }
        for r in html_e.xpath('//div[@class="result"]/table[@class="resulttable"]')
    ]
    return results


# 百分数转为int
def percent_to_int(string):
    if string.endswith('%'):
        return float(string.rstrip("%")) / 100
    else:
        return float(string)