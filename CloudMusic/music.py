import os
import requests
import execjs
import json

url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='

file = open('Cloudmusic.js','r').read()
Cloud_js = execjs.compile(file)
params_seckey = Cloud_js.call('as',2156424753)
# print(params_seckey)

headers = {
    'Referer':'https://music.163.com/',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Cookie':'NMTID=00OXKAOzP5HgGYzJEt2juObcnQwu6oAAAGP3Rx3vQ; _iuqxldmzr_=32; _ntes_nnid=68eae35b2f0dc80eaada6e43e78c9864,1717401586956; _ntes_nuid=68eae35b2f0dc80eaada6e43e78c9864; WEVNSM=1.0.0; WNMCID=xcypom.1717401587848.01.0; WM_TID=2VnAvaJZSRhAEVBVEVeV7%2BfmVvCXpEFy; ntes_utid=tid._.h%252FlmpLDbD2FFQhBURBOA%252B7L2FvSZWs8g._.0; sDeviceId=YD-q1lYuyGFr5JBAhUVUFOBuvL2U%2BXMS8tu; JSESSIONID-WYYY=c662lwdquKGuQr0CFVuugpu%5CO%2B1ncp%2Fi1t6vZ2tz%2BJfN0q9a%2Bo1PKyffS4X9hjXTsTY%2FdoNUjMYFzPvh7%2FP4vmTbeCnuOJHZF6ctQZozPrD1C1RJkeD0gg3WI3lCCIYAUy6kb7j%2F1l9PUqyZIUTQDbwP1uvJIng1h9xdrDkm20dwMR1q%3A1717479856611; WM_NI=EXjhtfvElr7S3bLi72OoU8If4VlY1OCG1EUsyrIQp7EqJato91tPGBZ8XupzZ2B6x2Fxy4KUmJImn8QW9qpgVHsiUkERiHoK5p7hCUJNE2yCiLWBCeNRCq71ZXyl49jteWM%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee84ce79ae958fafb77eed868aa7d85a938a9ab0d47fe9b58d8bc940fc968bb4c82af0fea7c3b92a8788a689f76eb69ba493b659f1be848ab63a8db19bd9cc6ef88aa4bab4458199ffa6d879bbae87b2f33d87af8682f765fbefbcb1c64a9ae89896f3729aee8ed7fb3a86a8b7d5ca5faf96878eed349389f792f36d9698bd8ad861878ea7a9ee41f7b0f989c25f8a928bd3fc49ab9499a3c26f8e8e8d92b63b9a88b78db733aaacabb8d037e2a3'
}

data = {
    'params':params_seckey['encText'],
    'encSecKey':params_seckey['encSecKey']
}

response = requests.post(url=url,data=data,headers=headers).text
song_url = json.loads(response)
music_id = song_url['data'][0]['id']
music_url = song_url['data'][0]['url']

# 检查music文件夹是否存在，如果不存在则创建
if not os.path.exists('music'):
    os.makedirs('music')

mp3 = requests.get(url=music_url,headers=headers).content

with open(f'music/{music_id}.mp3','wb') as file:
    file.write(mp3)