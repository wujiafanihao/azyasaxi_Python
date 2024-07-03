'''
Usage:
1. python3 -m pip install --user volcengine
2. python main.py
'''

import os
from volcengine.maas import MaasService, MaasException, ChatRole


def test_chat(maas, req):
    try:
        resp = maas.chat(req)
        print(resp)
        print(resp.choice.message.content)
        # 参考引用通过这个字段透传，URL是联网链接，idx指的是这个是第几个链接
        print(resp.choice.message.references)
    except MaasException as e:
        print(e)


def test_stream_chat(maas, endpoint_id, req):
    try:
        resps = maas.stream_chat(endpoint_id, req)
        for resp in resps:
            print(resp)
            print(resp.choice.message.content)
            # 流式接口，reference 列表随最后一个 message 返回
            print(resp.choice.message.references)
    except MaasException as e:
        print(e)


if __name__ == '__main__':
    maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')
    endpoint_id = "ep-20240515084737-5q2tt"
    maas.set_ak("AKLTMmM1ZGE2MDgxOTE2NGRiMjkxMDlhYTdhY2VhYmM4NjU")
    maas.set_sk("T0RKbU16UTRZalU0TWpNMk5EUmtPR0poWWpBNU1EVXpNR0V5WVRWak56aw==")

    # document: "https://www.volcengine.com/docs/82379/1099475"

    system_pmt = '''
    你是一位电视系统的测试工程师，
    需要编写和标注一些对影视、音乐、百科、闲聊问答等相关维度的多轮测试集,
    其中至少包含以下组合：
    1、影视/音乐/百科中的任意一个 + 闲聊问答

    具体要求：
    1、一轮对话的数量保持在3-5句
    2、答案和问题必须用四个横杠"----"隔开
    3、影视和音乐相关的测试问题，尽量考虑热门最新的
    '''

    words = '''
    帮我编写和标注一些电视上的多轮测试集，举例如下:
    case 1:
    听周杰伦的歌	
    他老婆是谁----外部服务内容是：周杰伦的老婆是昆凌。2014年11月17日，周杰伦公开与昆凌的恋情；2015年1月17日，周杰伦与昆凌在英国举行婚礼；2015年7月12日，周杰伦与昆凌的女儿出生；2022年5月6日，周杰伦与昆凌的三胎儿子出生。
    听他的晴天	
    这首歌创作于哪一年啊----外部服务内容是：《晴天》创作于 2003 年。这首歌是周杰伦的经典作品之一，具有独特的校园风旋律和清新的歌词，深受歌迷喜爱。

    case 2:
    看哈利波特	
    这个系列一共几部----"外部服务内容是：《哈利·波特》系列一共有 7 部，分别是：
    《哈利·波特与魔法石》
    《哈利·波特与密室》
    《哈利·波特与阿兹卡班的囚徒》
    《哈利·波特与火焰杯》
    《哈利·波特与凤凰社》
    《哈利·波特与混血王子》
    《哈利·波特与死亡圣器》。"
    看第三部----看《哈利·波特与阿兹卡班的囚徒》


    case 3:
    播放海贼王	
    这部动画片的原作者是谁----外部服务内容是：《海贼王》的原作者是尾田荣一郎。
    他还有哪些作品-----外部服务内容是：尾田荣一郎除了《海贼王》之外，还有一些短篇作品，比如《WANTED！尾田荣一郎短篇集》等。
    这部动画片讲了什么----外部服务内容是：《海贼王》讲述了路飞和他的伙伴们为了寻找传说中的宝藏"One Piece"而展开的冒险故事。


    case 4:
    播放三体
    这部剧改编自哪本书----外部服务内容是：《三体》电视剧改编自刘慈欣的同名科幻小说。
    他还写过哪些小说----外部服务内容是："刘慈欣除了《三体》还写过许多优秀小说，以下是一些比较知名的：
    - **《超新星纪元》**：讲述了一个世界被改变后的故事。
    - **《流浪地球》**：该作品已被改编成电影，获得了极大成功。
    - **《朝闻道》**：关于对宇宙终极真理的探索与追求。
    - **《微纪元》**：描绘了一个独特的未来世界。
    - **《乡村教师》**：将乡村教育与宇宙文明联系起来。
    - **《吞食者》** 等。"
    主角是谁演的----外部服务内容是：电视剧《三体》的主角汪淼由张鲁一饰演，史强由于和伟饰演。
    这部剧的主要剧情是什么----外部服务内容是：《三体》讲述了人类在面对外星文明"三体人"入侵时所经历的危机与抗争。

    case 5:
    奥特曼有多少个----"外部服务内容是：奥特曼的数量众多且不断有新的奥特曼推出。\n截至目前，有名有姓且被广泛认知的奥特曼大概有几十个，比如初代奥特曼、赛文奥特曼、杰克奥特曼、艾斯奥特曼、泰罗奥特曼、雷欧奥特曼、爱迪奥特曼、迪迦奥特曼等等。\n如果算上一些冷门或只在特定作品中出现的奥特曼，数量则会更多。"
    看第三个----看杰克奥特曼
    说错了看第四个----看艾斯奥特曼
    要免费的有吗
    快进3分钟
    
    case 6:
    看老版西游记	
    这里面孙悟空的扮演者是谁----外部服务内容是：1982版孙悟空的扮演者是六小龄童。
    他还出演过哪些作品----外部服务内容是：六小龄童还出演过《连城诀》等。

    特别注意：
    1、不要重复我的举例；
    2、其中外部服务内容需要你根据相关的知识来回答，不要编造，尽量长一点
    3、列举15组这样的case
    '''

    ronghe_sys = '''
    你是一个影视、音乐、百科问答等知识搜索助手，必须按我的要求回答问题
    '''
    ronghe_words = '''
    1、列举一些国内的著名喜剧演员及其代表作
    2、每个人的代表作需要2-3个
    3、每个代表作也需要比较完整的剧情简介
    4、每个演员用换行隔开
    
    '''
    req = {
        "model": {
            "endpoint_id": endpoint_id
        },
        "parameters": {
            "max_new_tokens": 2000,
            "temperature": 0.8
        },
        "messages": [
            {
                "role": ChatRole.SYSTEM,
                "content": ronghe_sys
            },
            {
                "role": ChatRole.USER,
                "content": ronghe_words
            },
        ],
        # 添加这个标记，以使用联网功能
        "plugins": ["browsing"],
    }

    test_chat(maas, req)
