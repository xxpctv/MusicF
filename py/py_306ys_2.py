#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import base64
import re
from urllib import request, parse
import urllib
import urllib.request
import time

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "360影视"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电视剧": "2",
			"电影": "1",
			"动漫": "4",
			"综艺":"3"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		result = {
			'list':[]
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		cat=''
		if 'cat' in extend.keys():
			cat=urllib.parse.quote(extend['cat'])
		year=''
		if 'year' in extend.keys():
			year=extend['year']
		area=''
		if 'area' in extend.keys():
			area=urllib.parse.quote(extend['area'])
		act=''
		if 'act' in extend.keys():
			act=urllib.parse.quote(extend['act'])
		Url='https://api.web.360kan.com/v1/filter/list?catid={0}&rank=rankhot&cat={2}&year={3}&area={4}&act={5}&size=35&pageno={1}'.format(tid,pg,cat,year,area,act)
		self.header['referer']='https://www.360kan.com/dianying/list?rank=rankhot&cat={1}&year={2}&area={3}&act={4}&pageno={0}'.format('2' if pg=='1' else int(pg)-1,cat,year,area,act)
		htmlTxt=self.webReadFile(urlStr=Url,header=self.header)
		videos=self.get_list(html=htmlTxt,types=tid)
		listCount=len(videos)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] =999999
		result['limit'] = listCount
		result['total'] = 99999
		return result
	def get_list(self,html,types):
		jRoot = json.loads(html)
		if jRoot['errno']=='0':
			return []
		videos = []
		data=jRoot['data']
		if data is None:
			return []
		jsonList=data['movies']
		for vod in jsonList:
			url = vod['id']
			title =vod['title']
			img='https:'+vod['cdncover']
			if len(url) == 0:
				continue
			guid="{0}###{1}###{2}###{3}".format(types,title,url,img)
			videos.append({
				"vod_id":guid,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":''
			})
		return videos
	def detailContent(self,array):		
		result = {}
		aid = array[0].split('###')
		tid=aid[0]#类型id
		title = aid[1]#片名
		urlId = aid[2]#URL
		logo = aid[3]#封面
		year=''#年份
		area=''
		actor=''
		director=''
		content=''
		vodItems=[]
		vod_play_from=[]#线路
		vod_play_url=[]#剧集
		url='https://api.web.360kan.com/v1/detail?cat={0}&id={1}'.format(tid,urlId)
		self.header['referer']='https://www.360kan.com'
		html=self.webReadFile(urlStr=url,header=self.header)

		if html.find('Success')>0:
			jRoot = json.loads(html)
			data=jRoot['data']
			vod_play_from_id=[t for t in data['playlink_sites']]
			vod_play_from=self.get_playlink(vod_play_from_id)
			title=data['title']
			year=data['pubdate']
			area='/'.join([v for v in data['area']])
			actor='/'.join([v for v in data['actor']])
			director='/'.join([v for v in data['director']])
			content=data['description']
			if 'allepidetail' in data:
				upinfo=int(data['upinfo'])
				Stepping=49 if upinfo>49 else upinfo-1
				for x in vod_play_from_id:
					starting=1
					end=starting+Stepping
					vodItems=[]

					while len(vodItems)<upinfo:

						url='https://api.web.360kan.com/v1/detail?cat={0}&id={1}&start={2}&end={3}&site={4}'.format(tid,urlId,starting,end,x)
						
						html=self.webReadFile(urlStr=url,header=self.header)
						
						if html.find('Success')<0:
							break
						jRoot = json.loads(html)
						data=jRoot['data']
						if 'allepidetail' in data:
							allepidetail=data['allepidetail']
							temporary=self.get_EpisodesList(html=allepidetail[x])
							for vod in temporary:
								vodItems.append(vod)
							joinStr = "#".join(vodItems)
							vodItems=[]
							vod_play_url.append(joinStr)
						
						if len(temporary)<1:
							break
						starting=end+1
						end+=Stepping
						if end>upinfo:
							end=upinfo	
			elif 'playlinksdetail' in data:
				playlinksdetail=data['playlinksdetail']
				keyName=list(playlinksdetail.keys())
				for l in keyName:
					temporary=playlinksdetail[l]
					url=temporary['default_url']
					vodItems.append(title+"$"+url)
					joinStr = "#".join(vodItems)
					temporary=[]
					vodItems=[]
					vod_play_url.append(joinStr)
				vod_play_from=self.get_playlink(keyName)
		
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":tid,
			"vod_year":year,
			"vod_area":area,
			"vod_remarks":"",
			"vod_actor":actor,
			"vod_director":director,
			"vod_content":content
		}
		vod['vod_play_from'] =  "$$$".join(vod_play_from)
		vod['vod_play_url'] = "$$$".join(vod_play_url)
		result = {
			'list':[
				vod
			]
		}
		return result
	def get_playlink(self,link):
		linkName={'xigua':'西瓜','douyin':'斗音','leshi':'乐视','youku':'优酷','imgo':'芒果','qiyi':'爱奇艺','qq':'腾讯','huanxi':'搜狐','bilibili1':'B站','cntv':'CCTV','cctv':'CCTV','m1905':'1905电影网'}
		returnName=[]
		for vod in link:
			returnName.append(linkName.get(vod,vod))
		return returnName
	def get_EpisodesList(self,html):
		videos = []
		for vod in html:
				url = vod['url']
				title =vod['playlink_num']
				videos.append(title+"$"+url)
		return videos	
	def searchContent(self,key,quick):
		key=urllib.parse.quote(key)
		url='https://api.so.360kan.com/index?force_v=1&kw={0}&from=&pageno=1&v_ap=1&tab=all'.format(key)
		self.header['referer']='https://so.360kan.com/?kw={0}&pageNum=1'.format(key)
		html=self.webReadFile(urlStr=url,header=self.header)
		#print(url)
		videos=self.get_list_search(html=html)
		#print(len(videos))
		result = {
			'list':videos
		}
		return result
	def get_list_search(self,html):
		jRoot = json.loads(html)
		if jRoot['msg']!='ok':
			return []
		videos = []
		data=jRoot['data']
		if data is None:
			return []
		longData=data['longData']
		if longData is None:
			return []
		jsonList=longData['rows']
		for vod in jsonList:
			url = vod['en_id']
			title =vod['titleTxt']
			img=vod['cover']
			cat_id=vod['cat_id']
			cat_name=vod['cat_name']
			if len(url) == 0:
				continue
			guid="{0}###{1}###{2}###{3}".format(cat_id,title,url,img)
			videos.append({
				"vod_id":guid,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":cat_name
			})
		return videos
	def playerContent(self,flag,id,vipFlags):
		result = {}
		headers = {
			'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
		}
		jx=1
		parse=1
		result["parse"] = parse#1=嗅探,0=播放
		result["playUrl"] = ''
		result["url"] = id
		result['jx'] = jx#1=VIP解析,0=不解析
		result["header"] = headers	
		return result
	config = {
		"player": {},
		"filter": {
		"2":[
		{"key":"cat","name":"类型","value":[{"n":"全部","v":""},{"n":"言情","v":"言情"},{"n":"剧情","v":"剧情"},{"n":"伦理","v":"伦理"},{"n":"喜剧","v":"喜剧"},{"n":"悬疑","v":"悬疑"},{"n":"都市","v":"都市"},{"n":"偶像","v":"偶像"},{"n":"古装","v":"古装"},{"n":"军事","v":"军事"},{"n":"警匪","v":"警匪"},{"n":"历史","v":"历史"},{"n":"励志","v":"励志"},{"n":"神话","v":"神话"},{"n":"谍战","v":"谍战"},{"n":"青春","v":"青春"},{"n":"家庭","v":"家庭"},{"n":"动作","v":"动作"},{"n":"情景","v":"情景"},{"n":"武侠","v":"武侠"},{"n":"科幻","v":"科幻"},{"n":"其他","v":"其他"}]},
		{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"更早","v":"lt_year"}]},
		{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"泰国","v":"泰国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"美国","v":"美国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"}]}
		],
		"1":[
		{"key":"cat","name":"类型","value":[{"n":"全部","v":""},{"n":"喜剧","v":"喜剧"},{"n":"爱情","v":"爱情"},{"n":"动作","v":"动作"},{"n":"恐怖","v":"恐怖"},{"n":"科幻","v":"科幻"},{"n":"剧情","v":"剧情"},{"n":"犯罪","v":"犯罪"},{"n":"偶像","v":"偶像"},{"n":"奇幻","v":"奇幻"},{"n":"战争","v":"战争"},{"n":"悬疑","v":"悬疑"},{"n":"动画","v":"动画"},{"n":"文艺","v":"文艺"},{"n":"纪录","v":"纪录"},{"n":"传记","v":"传记"},{"n":"歌舞","v":"歌舞"},{"n":"古装","v":"古装"},{"n":"历史","v":"历史"},{"n":"惊悚","v":"惊悚"},{"n":"伦理","v":"伦理"},{"n":"其他","v":"其他"}]},
		{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"更早","v":"lt_year"}]},
		{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"泰国","v":"泰国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"美国","v":"美国"},{"n":"英国","v":"英国"},{"n":"法国","v":"法国"},{"n":"德国","v":"德国"},{"n":"印度","v":"印度"},{"n":"其他","v":"其他"}]}
		],
		"4":[
		{"key":"cat","name":"类型","value":[{"n":"全部","v":""},{"n":"热血","v":"热血"},{"n":"科幻","v":"科幻"},{"n":"美少女","v":"美少女"},{"n":"魔幻","v":"魔幻"},{"n":"经典","v":"经典"},{"n":"励志","v":"励志"},{"n":"少儿","v":"少儿"},{"n":"冒险","v":"冒险"},{"n":"搞笑","v":"搞笑"},{"n":"推理","v":"推理"},{"n":"恋爱","v":"恋爱"},{"n":"治愈","v":"治愈"},{"n":"幻想","v":"幻想"},{"n":"校园","v":"校园"},{"n":"动物","v":"动物"},{"n":"机战","v":"机战"},{"n":"亲子","v":"亲子"},{"n":"儿歌","v":"儿歌"},{"n":"运动","v":"运动"},{"n":"悬疑","v":"悬疑"},{"n":"怪物","v":"怪物"},{"n":"战争","v":"战争"},{"n":"益智","v":"益智"},{"n":"青春","v":"青春"},{"n":"童话","v":"童话"},{"n":"竞技","v":"竞技"},{"n":"动作","v":"动作"},{"n":"社会","v":"社会"},{"n":"友情","v":"友情"},{"n":"真人版","v":"真人版"},{"n":"剧场版","v":"电影版"}]},
		{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"更早","v":"lt_year"}]},
		{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"日本","v":"日本"},{"n":"美国","v":"美国"}]}
		],
		"3":[
		{"key":"cat","name":"类型","value":[{"n":"全部","v":""},{"n":"脱口秀","v":"脱口秀"},{"n":"真人秀","v":"真人秀"},{"n":"搞笑","v":"搞笑"},{"n":"选秀","v":"选秀"},{"n":"八卦","v":"八卦"},{"n":"访谈","v":"访谈"},{"n":"情感","v":"情感"},{"n":"生活","v":"生活"},{"n":"晚会","v":"晚会"},{"n":"音乐","v":"音乐"},{"n":"职场","v":"职场"},{"n":"美食","v":"美食"},{"n":"时尚","v":"时尚"},{"n":"游戏","v":"游戏"},{"n":"少儿","v":"少儿"},{"n":"纪实","v":"纪实"},{"n":"科教","v":"科教"},{"n":"曲艺","v":"曲艺"},{"n":"歌舞","v":"歌舞"},{"n":"财经","v":"财经"},{"n":"汽车","v":"汽车"},{"n":"播报","v":"播报"},{"n":"其他","v":"其他"}]},
		{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"欧美","v":"欧美"}]}
		]
		}
		}
	header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
	    'referer':'https://www.360kan.com/dianying/list?rank=rankhot&cat=&year=&area=&act=&pageno=2',
	    'Host':'api.web.360kan.com'
	}
	def webReadFile(self,urlStr,header):
		html=''
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode('utf-8')
		#print(Host)
		return html
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
