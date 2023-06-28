import requests
import urllib
import hashlib


# key文件中存放AK和SK，第一行为AK，第二行为SK，两者之间用换行符分隔
# AK和SK均为百度地图API提供
def get_key():
    with open('key', 'r') as f:
        return f.read()

def get_country_baiduapi(lat, lon):
    # encoding:utf-8
    # 根据您选择的AK以为您生成调用代码
    # 检测您当前的AK设置了sn检验，本示例中已为您生成sn计算代码
    # encoding:utf-8
    # python版本为3.6.2

    # 服务地址
    host = "https://api.map.baidu.com"

    # 接口地址
    uri = "/reverse_geocoding/v3"

    key = get_key().split('\n')

    # 此处填写你在控制台-应用管理-创建应用后获取的AK
    ak = key[0]

    # 此处填写你在控制台-应用管理-创建应用时，校验方式选择sn校验后生成的SK
    sk = key[1]

    # 设置您的请求参数
    params = {
        "ak": ak,
        "output": "json",
        "coordtype": "wgs84ll",
        "extensions_poi": "0",
        "location": str(lat) + "," + str(lon)

    }

    # 拼接请求字符串
    paramsArr = []
    for key in params:
        paramsArr.append(key + "=" + params[key])

    queryStr = uri + "?" + "&".join(paramsArr)

    # 对queryStr进行转码，safe内的保留字符不转换
    encodedStr = urllib.request.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")

    # 在最后直接追加上您的SK
    rawStr = encodedStr + sk

    # 计算sn
    sn = hashlib.md5(urllib.parse.quote_plus(rawStr).encode("utf8")).hexdigest()

    # 将sn参数添加到请求中
    queryStr = queryStr + "&sn=" + sn

    # 请注意，此处打印的url为非urlencode后的请求串
    # 如果将该请求串直接粘贴到浏览器中发起请求，由于浏览器会自动进行urlencode，会导致返回sn校验失败
    url = host + queryStr
    response = requests.get(url)
    if response:
        return response.json()['result']['addressComponent']['country']