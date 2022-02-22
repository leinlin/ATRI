from random import choice, randint

from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.helpers import Cooldown
from nonebot.adapters.onebot.v11 import MessageSegment
from .data_source import Funny


get_laugh = Funny().on_command("来句笑话", "隐晦的笑话...")


@get_laugh.handle()
async def _get_laugh(bot: Bot, event: MessageEvent):
    user_name = event.sender.nickname or "该裙友"
    await get_laugh.finish(await Funny().idk_laugh(user_name))

never_give_up = Funny().on_regex(r"太难了", "人不能随便就半途而废呢")
@never_give_up.handle()
async def _never_give_up(bot: Bot, event: MessageEvent):
    await never_give_up.finish(MessageSegment.image(
                    file="https://cdn.jsdelivr.net/gh/leinlin/CDN@master/project/ATRI/nan.jpg"
                ))


_fake_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])


fake_msg = Funny().on_command(
    "/fakemsg", "伪造假转发内容，格式：qq-name-content\n可构造多条，使用空格隔开，仅限群聊"
)


@fake_msg.handle([Cooldown(10, prompt=_fake_flmt_notice)])
async def _ready_fake(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("content", args)


@fake_msg.got("content", "内容呢？格式：qq-name-content\n可构造多条，以上仅为一条，使用空格隔开")
async def _deal_fake(
    bot: Bot, event: GroupMessageEvent, content: str = ArgPlainText("content")
):
    group_id = event.group_id
    try:
        node = Funny().fake_msg(content)
    except Exception:
        await fake_msg.finish("内容格式错误，请检查（")

    try:
        await bot.send_group_forward_msg(group_id=group_id, messages=node)
    except Exception:
        await fake_msg.finish("构造失败惹...可能是被制裁了（")


eat_what = Funny().on_regex(r"大?[今明后]天(.*?)吃[什啥]么?", "我来决定你吃什么！")


@eat_what.handle([Cooldown(15, prompt="慢慢吃，不要贪心哦！")])
async def _eat_what(event: MessageEvent):
    msg = str(event.get_message())
    user_name = event.sender.nickname or "裙友"
    eat = await Funny().eat_what(user_name, msg)
    await eat_what.finish(Message(eat))
