import random
import time, datetime
import requests
from jsonpath import jsonpath
from MsgBot import WxComBot
import os

SIGN_URL = 'https://shop.skycolorful.com/api/User/SignV2'
GET_POST_URL = 'https://shop.skycolorful.com/api/Bbs/GetPostingList?Page=1&Size=10&ModuleId=%20%20%20%20&IsNewest=true&IsEssence=false'
POST_LIKE_URL = 'https://shop.skycolorful.com/api/Bbs/Like'
USER_INFO_URL = 'https://shop.skycolorful.com/api/User/GetUserInfo'
SHOP_URL = 'https://shop.skycolorful.com/api/PointExchange/GetPointExchange?Page=1&Limit=10&GradeId=6'

TOKEN = os.environ.get('token')
XTOKEN = os.environ.get('xtoken')
APPID = os.environ.get('appid')
SIGN = os.environ.get('sign')

corp_id = os.environ.get('corp_id')
corp_secret = os.environ.get('corp_secret')
corp_user = os.environ.get('corp_user')


TICKS = ticks = str(int(time.time() * 1000))
print(TOKEN)
POST_IDS_FILE = 'static/post_id.json'
headers = {
    "X-Authorization": XTOKEN,
    "Authorization": TOKEN,
    'AppId': APPID,
    "Sign": SIGN,
    "Ticks": TICKS,
    "requestId": '1774cef6-0311-4ded-bf2d-5fa4d589f5a3',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) XWEB/9105"
}


def write_post_ids(response):
    post_ids = jsonpath(response, '$..Id')
    if post_ids and not isinstance(post_ids, bool):
        print(post_ids)
        with open(POST_IDS_FILE, 'w+') as file:
            file.write(str(post_ids))
    else:
        raise ValueError('获取post_id失败')


def read_file(file_name, encoding='gbk'):
    with open(file_name, 'r+', encoding=encoding) as file:
        content = file.read()
    if content is None:
        raise "文件内容为空"
    return content


def request_url(url, headers, method='post', data=None, task_name=''):
    response = requests.request(method=method, url=url, headers=headers, json=data)
    if 200 != response.status_code and response.json()['Code'] != 0:
        raise BaseException(f"{task_name}任务访问失败{response.json()}用户token{TOKEN}")
    return response.json()


def sky_sign():
    data = {}
    response = request_url(url=SIGN_URL, headers=headers, data=data, task_name='每日签到')
    # assert response['code'] == 0
    return response['Message']


def query_post():
    data = {
        "page": 1,
        "size": 10,
        "IsNewest": True,
        "IsEssence": False
    }
    response = request_url(GET_POST_URL, headers=headers, method='get', data=data, task_name='获取帖子id')
    Ids = jsonpath(response, '$..Id')
    if not Ids or isinstance(Ids, bool):
        return '获取帖子Id失败'
    write_post_ids(response)
    return '成功获取post_ids'


def post_like(list_count, post_ids):
    data = {"postId": "6a5e1943-cb1e-41d7-92e4-05d39f2bb1ef", "postReplyId": "0"}
    for _ in range(list_count):
        j = random.randrange(0, len(post_ids))
        data["id"] = post_ids[j]
        response = request_url(POST_LIKE_URL, headers=headers, data=data, task_name='帖子点赞')
        time.sleep(random.randint(5, 10))
    return '每日点赞任务成功~'


def user_info():
    """
    获取用户信息
    :return:
    """
    response = request_url(url=USER_INFO_URL, headers=headers, method='get', task_name='获取用户详情')
    point = jsonpath(response, '$..Point')
    if not point or isinstance(point, bool):
        return '获取用户积分信息失败'
    return point


# CRAZEKFC？
def thursday_exchange():
    '''
    判断是否是星期4
    如果是则请求查询当天的物品内容,如果不是则退出判断;

    :return:
    '''

    is_thursday = datetime.date.today().weekday() == 2
    if is_thursday:
        response = request_url(url=SHOP_URL, method='get', headers=headers, data='data', task_name='兑换物品推送')
        goods_name = jsonpath(response, '$..Name')
        print(goods_name)
        if not goods_name or isinstance(goods_name, bool):
            return '获取物品信息失败'
        return goods_name


def daily_task():
    """
    每日任务
    :return:
    """
    # 更新ids
    thursday_exchange()
    query_post()
    # 获取post_ids内容
    with open(POST_IDS_FILE, 'r', encoding='utf-8') as file:
        post_ids = file.read()
    print(post_ids)
    # 每日签到一次
    sign_result = sky_sign()
    post_like_result = post_like(5, post_ids)
    user_point_result = user_info()
    wx_msg = f"'\n'{post_like_result}  + '\n'{sign_result} + '\n' {user_point_result} "
    wx_com_bot = WxComBot(corp_id, corp_secret)
    wx_com_bot.send_msg_text('1000002', "sky-color-sign" + wx_msg, corp_user)


if __name__ == '__main__':
    daily_task()
