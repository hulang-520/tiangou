import requests
import math
import yaml
from datetime import date, datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header


# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


config = getYmlConfig()
application = config['application']
girlfriend = config['girlfriend']


# 获取天气信息，今天的和明天的#默认只有2000额度
def getWeather(city, appid=application['weather']['appid'], appsecret=application['weather']['appsecret']):
    url = 'https://yiketianqi.com/api?version=v1&city={city}&appid={appid}&appsecret={appsecret}'.format(city=city,
                                                                                                             appid=appid,
                                                                                                             appsecret=appsecret)
    res = requests.get(url)
    date = res.json()['data']
    return {
        'today': date[0],
        'tomorrow': date[1]
    }


# 获取土味情话，有时候很智障 #修改api 女朋友不喜欢删了
#def getSweetWord():
    url = 'http://api.tianapi.com/txapi/saylove/index?key=ce596834fa7e8c5d9d21dee24aa98fc5'
    res = requests.get(url)
    return res.json()['newslist'][0]['content']
#tiangou日记
def tiangou():
    url = 'https://api.muxiuge.cn/API/tiangou.php'
    res = requests.get(url=url)
    return res.json()['text']

tiangou()
# 模板消息，有能力的话，可以自己修改这个模板
def getMessage():
    now = datetime.now()#获取当前时间 2021-08-13 15:53:24.017199
    start = datetime.strptime(girlfriend['start_love_date'], "%Y-%m-%d")#获取表格填写时间
    days = (now - start).days#得到在一起天数
    city = girlfriend['city']#获取填写城市
    weather = getWeather(city=city)#得到当天和昨天数据
    today = weather['today']#获取今天时间
    tomorrow = weather['tomorrow']#获取明天时间
    today_avg = (int(today['tem1'][:-1]) + int(today['tem2'][:-1])) / 2#获取今天温度
    tomorrow_avg = (int(tomorrow['tem1'][:-1]) + int(tomorrow['tem2'][:-1])) / 2#获取明天天气
    wdc = ''
    if today_avg > tomorrow_avg:
        wdc += '下降'
        wdc += str(abs(tomorrow_avg - today_avg)) + "℃"
    elif math.isclose(tomorrow_avg, today_avg):
        wdc += '保持不变'
    else:
        wdc += '上升'
        wdc += str(abs(tomorrow_avg - today_avg)) + "℃"
    return "❥(^_-) " + config['girlfriend'].get("nickname") + \
           "\n今天是 " + today['date'] + " " + today['week'] + \
           "\n" + girlfriend['date_msg'] % days + \
           "\n" + "\\ 温馨提示" + \
           "\n" + city + " 明日天气：" + tomorrow['wea'] + \
           "\n" + "气温：" + tomorrow['tem2'][:-1] + "/" + tomorrow['tem1'][:-1] + "℃" + \
           "\n" + "与今天相比，明天的平均气温将会：" + wdc + \
           "\n" + " 穿衣建议：" + tomorrow['index'][3]['desc'] + \
           "\n" + "xx舔狗日记: "  + tiangou() + \
           "\n"+"\n" + "以上信息来自 " + girlfriend["sweet_nickname"] + "mua-mua-mua" + ""


def SendMessage(qmsg):
    
    mail_msg = getMessage()
    if qmsg == '':
        print("未配置QMSG酱，消息不会推送")
        return False
    data = {
        'token': qmsg,
        'msg': "你的每日xx推送"+"\n"+mail_msg,
        }
    try:
        res = requests.post(
            url='https://qmsg.zendee.cn/send/{}'.format(qmsg), data=data)
    except:
        print('发送失败')

def main_handler(event, context):
    try:
        SendMessage(application['qmsgd']['qmsg'])
    except Exception as e:
        print('出现错误')
        raise e
    else:
        return 'success'


if __name__ == '__main__':
    print(main_handler({}, {}))
