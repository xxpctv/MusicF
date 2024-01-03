#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import base64
import re
from urllib import request, parse
import urllib
import urllib.request
import ssl
from lxml import etree
ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证

class Spider(Spider):  # 元类 默认的元类 type
	def getName():
		return "放美剧"
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
			"美剧": "1",
			"电视剧":"10",
			"动漫":"15",
			"最近更新":"47",
			"排行榜":"46"
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
		htmlTxt=self.custom_webReadFile(urlStr='https://www.fmeiju.com/',header=self.header)
		root = self.html(htmlTxt)
		# root = etree.HTML(htmlTxt)
		nodes = root.xpath('//a[@class="link"]')
		videos=[]
		head="https://www.fmeiju.com"
		for a in nodes:
			title=a.xpath('./@title')[0]
			if len(a.xpath('./div[@class="pic"]/div[@class="img"]/img/@data-original'))<1 or len(a.xpath("./@href"))<1:
				continue
			url=a.xpath("./@href")[0]
			img=a.xpath('./div[@class="pic"]/div[@class="img"]/img/@data-original')[0]
			if url.find('://')<1:
				url=head+url
			if img.find('://')<1:
				img=head+img
			vod_id="{0}###{1}###{2}".format(title,url,img)
			videos.append({
				"vod_id":vod_id,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":''
			})
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		Url='https://www.fmeiju.com/vodlist/{0}_{1}.html'.format(tid,pg)
		if tid=='46' or tid=='47':
			Url='https://www.fmeiju.com/list/{0}.html'.format(tid)
		htmlTxt=self.custom_webReadFile(urlStr=Url,header=self.header)
		root = self.html(htmlTxt)
		# root = etree.HTML(htmlTxt)
		nodes = root.xpath("//div/div[@class='channel clearfix']/ul[@class='cul']/li")

		videos = self.custom_list(liList=nodes)
		pagecount=0 if len(videos)<29 else int(pg)+1
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] =pagecount if int(tid)<45 else 1
		result['limit'] = 90
		result['total'] = 999999
		return result
	def detailContent(self,array):
		aid = array[0].split('###')
		idUrl=aid[1]
		title=aid[0]
		pic=aid[2]
		url=idUrl
		htmlTxt =  self.custom_webReadFile(urlStr=url,header=self.header)
		# htmlTxt=self.readFile(filePath=r'D:\1.txt')
		
		line=self.custom_RegexGetTextLine(Text=htmlTxt,RegexText=r'<li id="tab1\d" onclick="setTab\(.+?\)"><i class=".+?"></i>(.+?)</li>',Index=1)
		
		if len(line)<1:
			return  {'list': []}
		playFrom = []
		videoList=[]
		vodItems = []
		circuit=self.custom_lineList(Txt=htmlTxt,mark=r'<ul class="playul">',after='</ul>')
		playFrom=line
		for v in circuit:
			vodItems = self.custom_EpisodesList(html=v,RegexText=r"<li><a title='(?P<title>.+?)' href='(?P<url>.+?)'"+' target="_self">.+?</a></li>')
			joinStr = "#".join(vodItems)
			videoList.append(joinStr)
		vod_play_from='$$$'.join(playFrom)
		vod_play_url = "$$$".join(videoList)

		typeName=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<span>类型：</span>(.+?)</em>',Index=1)
		year=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<a href="/search.php\?searchword=(\d{4})">\d{4}</a>',Index=1)
		area=''
		act=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'主演：(.+?)导演：',Index=1)
		dir=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'导演：(.+?)类型：',Index=1)
		cont=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<div class="cdes clearfix">(.+?)</div>',Index=1)
		vod = {
			"vod_id": array[0],
			"vod_name": title,
			"vod_pic": pic,
			"type_name":self.custom_removeHtml(txt=typeName),
			"vod_year": self.custom_removeHtml(txt=year),
			"vod_area": area,
			"vod_remarks": '',
			"vod_actor":  self.custom_removeHtml(txt=act),
			"vod_director": self.custom_removeHtml(txt=dir),
			"vod_content": self.custom_removeHtml(txt=cont)
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list': [
				vod
			]
		}
		return result

	def searchContent(self,key,quick):
		data="searchword="+urllib.parse.quote(key)
		payUrl="https://www.fmeiju.com/search.php"
		req = request.Request(url=payUrl, data=bytes(data, encoding='utf8'),headers=self.header, method='POST')
		response = request.urlopen(req)
		# from lxml import etree
		htmlTxt=response.read().decode('utf-8')
		root = self.html(htmlTxt)
		nodes = root.xpath("//div[@class='searchlist']/ul[@class='cul clearfix']/li")
		videos=self.custom_list_xpath(liList=nodes)
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		Url=id
		htmlTxt =self.custom_webReadFile(urlStr=Url,header=self.header)
		parse=0
		UrlStr=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'var now="(.+?)"',Index=1)
		if UrlStr.find('.m3u8')<2:
			Url=id
			parse=1
		else:
			Url=UrlStr
		result["parse"] = parse#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = Url
		# result['jx'] = jx#VIP解析,0=不解析、1=解析
		result["header"] = ''	
		return result


	config = {
		"player": {},
		"filter": {}
		}
	header = {
		"Referer": 'https://www.fmeiju.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
		"Host":'www.fmeiju.com'
		}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
		#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	#分类取结果
	def custom_list(self,liList):
		videos = []
		head="https://www.fmeiju.com"
		renew=''
		for vod in liList:
			a=vod.xpath('./a[@class="link"]')
			for v in a:
				title=v.xpath('./@title')[0]
				img=v.xpath('./div[@class="pic"]/div[@class="img"]/img/@data-original')[0]
				url=v.xpath("./@href")[0]
				if url.find('://')<1:
					url=head+url
				if img.find('://')<1:
					img=head+img
				try:
					temporary=v.xpath('./div[@class="pic"]/div[@class="info"]/p[@class="zt"]')
					if len(temporary)<1:
						temporary=v.xpath('./div[@class="pic"]/div[@class="img"]/span[@class="state"]/span[@class="ico lzpng ztpng"]')
						if len(temporary)>0:
							renew=temporary[0].text
						else:
							renew=temporary[0].text
				except:
					pass
				vod_id="{0}###{1}###{2}".format(title,url,img)
				videos.append({
					"vod_id":vod_id,
					"vod_name":title,
					"vod_pic":img,
					"vod_remarks":''
				})
		return [i for n, i in enumerate(videos) if i not in videos[:n]]
		#访问网页
	def custom_webReadFile(self,urlStr,header=None,codeName='utf-8'):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode(codeName)
		return html
	#判断是否要调用vip解析
	def custom_ifJx(self,urlTxt):
		Isjiexi=0
		RegexTxt=r'(youku.com|v.qq|bilibili|iqiyi.com)'
		if self.custom_RegexGetText(Text=urlTxt,RegexText=RegexTxt,Index=1)!='':
			Isjiexi=1
		return Isjiexi
	#取集数
	def custom_EpisodesList(self,html,RegexText):
		ListRe=re.finditer(RegexText, html, re.M|re.S)
		videos = []
		head="https://www.fmeiju.com"
		for vod in ListRe:
			url = vod.group('url')
			title =vod.group('title')
			if len(url) == 0:
				continue
			videos.append(title+"$"+head+url)
		return videos
	#取剧集区
	def custom_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit	
	#正则取文本,返回数组	
	def custom_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	def custom_mid(self,txt,startStr,endStr):
		start=txt.find(startStr)
		end=txt.find(endStr,start)
		if start<0 or end>len(txt) or end<start:
			return ''
		str=txt[start+len(startStr):end]
		return str
	#删除html标签
	def custom_removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")
	def custom_list_xpath(self,liList):
		videos = []
		head="https://www.fmeiju.com"
		for vod in liList:
			a=vod.xpath('./a[@class="link"]')
			for v in a:
				title=v.xpath('./@title')[0]
				img=v.xpath('./div[@class="pic"]/div[@class="img"]/img/@data-original')[0]
				url=v.xpath("./@href")[0]
				# renew=v.xpath('./div[@class="pic"]/div[@class="info"]/p[@class="zt"]')[0].text
				videos.append({
					"vod_id":"{0}###{1}###{2}".format(title,head+url,head+img),
					"vod_name":title,
					"vod_pic":img,
					"vod_remarks":''
				})
		return [i for n, i in enumerate(videos) if i not in videos[:n]]


# T=Spider()
# l=T.searchContent(key='柯南',quick='')
# l=T.homeVideoContent()
# # extend={'types':'netflix',"area":"韩国","year":"2023","lang":"韩语","sort":"score"}
# l=T.categoryContent(tid='1',pg='1',filter=False,extend={})
# for x in l['list']:
# 	print(x['vod_id'])