import random
import time
import requests
from jsonpath import jsonpath
from datetime import datetime
import json
from MsgBot import WxComBot
import os

SIGN_URL = 'https://interface.skycolorful.com/api/User/Sign'
GET_POST_URL = 'https://interface.skycolorful.com/api/Article/GetArticlePage'
POST_DETAILS_URL = 'https://interface.skycolorful.com/api/Article/GetArticleDetail'
POST_COMMENT_URL = 'https://interface.skycolorful.com/api/Comment/CreateComment'
POST_LIKE_URL = 'https://interface.skycolorful.com/api/Article/ArticleLike'
USER_INFO_URL = 'https://interface.skycolorful.com/Api/User/GetUserInfo'
POST_BROWSER_URL = 'https://interface.skycolorful.com/api/Article/IncreArticlePoint'
USER_POINT_LOG = 'https://interface.skycolorful.com/api/User/UserPointLog'

#os.environ.setdefault('TOKEN', "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoi57uP5byA5q2j5b6I5bm2IiwianRpIjoiOTI4NzUiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiIwNS8yMC8yMDI0IDA5OjQ2OjQ2IiwibmJmIjoxNzEzNTc3NjA2LCJleHAiOjE3MTYxNjk2MDYsImlzcyI6IkNvcmVTaG9wUHJvZmVzc2lvbmFsIiwiYXVkIjoiQ29yZUNtcyJ9.G4ou71kLGu3q2chrrz8iBaLFYhjdYOS8b9S7hsayFZU")
TOKEN = os.environ['TOKEN']
print(TOKEN)
POST_IDS_FILE = 'static/post_id.json'
COMMENT_FILE = 'static/comment.txt'

headers = {
    "Host": "interface.skycolorful.com",
    "Connection": "keep-alive",
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) XWEB/9105"
}


def write_post_ids(response):
    post_ids = jsonpath(response, '$..id')
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


def request_url(url, headers, data=None, task_name=''):
    response = requests.post(url, headers=headers, json=data)
    if 200 != response.status_code and response.json()['code'] != 0:
        raise BaseException(f"{task_name}任务访问失败{response.json()}'\n'"
                            f"{TOKEN}")
    return response.json()


def sky_sign():
    data = {}
    response = request_url(SIGN_URL, headers=headers, data=data, task_name='每日签到')
    # assert response['code'] == 0
    return response['msg']


def query_post():
    data = {
        "page": 1,
        "limit": 50,
        "id": 0
    }
    response = request_url(GET_POST_URL, headers=headers, data=data, task_name='查找页面总数')
    total_pages = jsonpath(response, '$..totalPages')
    if not total_pages or isinstance(total_pages, bool):
        return '获取total_pages失败'
    write_post_ids(response)
    if total_pages[0] > 1:
        for i in range(2, total_pages[0] + 1):
            data['page'] = i
            response = request_url(GET_POST_URL, headers=headers, data=data, task_name='获取帖子id')
            write_post_ids(response)
    return '成功获取post_ids'


def post_details(view_count, post_ids):
    data = {
        "id": "30682"
    }
    for _ in range(view_count):
        j = random.randrange(0, len(post_ids))
        data["id"] = post_ids[j]
        post_details_rsp = request_url(POST_DETAILS_URL, headers=headers, data=data, task_name='浏览帖子详情')
        time.sleep(random.randrange(10, 20))
        view_point_rsp = post_browse(data)
    return '每日帖子浏览成功~！'


def post_comment(comment_count, comment_contents, post_ids):
    data = {
        "targetId": 30682,
        "level": 1,
        "type": 1,
        "content": "厉害啊，我之前用的一般"
    }
    print(type(comment_contents))
    for _ in range(comment_count):
        j = random.randrange(0, len(comment_contents))
        k = random.randrange(0, len(post_ids))
        data['content'] = comment_contents[j]
        data['targetId'] = post_ids[k]
        response = request_url(POST_COMMENT_URL, headers=headers, data=data, task_name='回复帖子内容')
        time.sleep(random.randrange(5, 10))
    return '每日随机回复成功~'


def post_like(list_count, post_ids):
    data = {
        "id": "30682",
        "data": True
    }
    for _ in range(list_count):
        j = random.randrange(0, len(post_ids))
        data["id"] = post_ids[j]
        data["data"] = False
        response = request_url(POST_LIKE_URL, headers=headers, data=data, task_name='帖子点赞')
        data["data"] = True
        response = request_url(POST_LIKE_URL, headers=headers, data=data, task_name='帖子点赞')
        time.sleep(random.randint(5, 10))
    return '每日点赞任务成功~'


def user_info():
    """
    获取用户信息
    :return:
    """
    response = request_url(USER_INFO_URL, headers=headers)
    return response


def user_point_log():
    data = {
        "page": 1,
        "limit": 15,
        "where":
            "{type: 1,flag:1}"
    }
    response = request_url(USER_POINT_LOG, headers=headers, data=data, task_name='积分获取记录')
    curr_date = datetime.now().strftime("%Y-%m-%d")
    # print(curr_date)
    # $..children[?(@.role=="group")]
    # print(response['data']['data'])
    # jsonpath提取不到的情况下可以考虑手写路径
    nums = [item['num'] for item in response['data']['data'] if item['createTime'].startswith(f'{curr_date}')]
    # print(nums)
    if not nums or isinstance(nums, bool):
        return '获取详细积分失败~'
    else:
        total_nums = sum(nums)
    return f'今天获取的积分为{total_nums},应获取积分为58'


def post_browse(data):
    """
    获取浏览积分
    :return:
    """
    response = request_url(POST_BROWSER_URL, headers=headers, data=data, task_name='获取浏览积分')
    return response


def daily_task():
    """
    每日任务
    :return:
    """
    # 更新ids
    query_post()
    # 获取post_ids内容
    post_ids = json.loads(read_file(POST_IDS_FILE))
    comment_contents = read_file(COMMENT_FILE, 'utf-8')
    comment_contents = [comment for comment in comment_contents.split('\n')]
    # 每日签到一次
    sign_result = sky_sign()
    # 浏览帖子+积分获取
    post_view_result = post_details(2, post_ids)
    # 随机回复3帖子
    post_comment_result = post_comment(3, comment_contents, post_ids)
    # 随机点赞帖子5次
    post_like_result = post_like(5, post_ids)
    # 获取当前积分记录信息
    user_point_result = user_point_log()
    wx_msg = f"{post_view_result}'\n'{post_like_result} + '\n'{post_comment_result} + '\n'{sign_result} + '\n' {user_point_result} "
    # print(user_point_result)
    wx_com_bot = WxComBot('ww85eb6097649bfa4d', '_uQAPvqzla0FMlPx-QZS0jFFQ8AUWQ3J8H8o86ysSPQ')
    wx_com_bot.send_msg_text('1000002', "sky-color-sign" + wx_msg, 'WuDingKang')


if __name__ == '__main__':
    daily_task()
