import re
import json
from random import choice, random
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import MessageEvent, Message,MessageSegment
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .data_source import Encrypt, Utils, Yinglish


roll = Utils().on_command("/roll", "骰子~用法：1d10 或 2d10+2d10+more")


@roll.handle()
async def _ready_roll(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("roll", args)


@roll.got("roll", "参数呢？！格式：1d10 或 2d10+2d10+more")
async def _deal_roll(roll_msg: str = ArgPlainText("roll")):
    match = re.match(r"^([\dd+\s]+?)$", roll_msg)

    if not match:
        await roll.finish("阿——！参数不对！格式：1d10 或 2d10+2d10+more")

    msg = Utils().roll_dice(roll_msg)
    await roll.finish(msg)


encrypt_en = Utils().on_command("加密", "我们之间的秘密❤")

@encrypt_en.got("encr_en_text", "内容呢？！")
async def _deal_en(event: MessageEvent):
    replyArray = []
    for v in event.get_message():
        if v.type == "image":
            replyArray.append({"type":'image', "data":{'file':v.data['url']}})
        elif v.type == "text":
            replyArray.append({"type":'text', "data":{'text':v.data['text']}})

    text = json.dumps(replyArray)
    is_ok = len(text)
    if is_ok < 10:
        await encrypt_en.reject("太短不加密！")
    en = Encrypt()
    result = en.encode(text)
    await encrypt_en.finish(result)


encrypt_de = Utils().on_command("解密", "解开我们的秘密❤")


@encrypt_de.handle()
async def _ready_de(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("encr_de_text", args)


@encrypt_de.got("encr_de_text", "内容呢？！")
async def _deal_de(text: str = ArgPlainText("encr_de_text")):
    en = Encrypt()
    result = en.decode(text)
    replyArray = json.loads(result)
    msgArray = []
    for v in replyArray:
        msgArray.append(MessageSegment(type=v["type"], data=v["data"]))
    
    await encrypt_de.finish(msgArray)



sepi = Utils().on_command("涩批一下", "将正常的句子涩一涩~")


_sepi_flmt_notice = choice(["涩批爬", "✌🥵✌"])


@sepi.handle([Cooldown(3, prompt=_sepi_flmt_notice)])
async def _ready_sepi(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("sepi_text", args)


@sepi.got("sepi_text", "内容呢？！")
async def _deal_sepi(event: MessageEvent, msg: str = ArgPlainText("sepi_text")):
    user_id = event.get_user_id()
    if len(msg) < 4:
        await sepi.finish("这么短？涩不起来！")

    result = Yinglish.deal(msg, random())
    await sepi.finish(result)
