var rule = {
    title:'JRKAN直播',
    host:'https://www.jryyds.com/',
    url:'/fyclass',
    class_name:'直播赛事✨时间',
    class_url:'/',
    推荐:'*',
    一级:"js:var items=[];pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;var html=request(input);var tabs=pdfa(html,'body&&.loc_match:eq(2) ul');tabs.forEach(function(it){var pz=pdfh(it,'.name:eq(1)&&Text');var ps=pdfh(it,'.name:eq(0)&&Text');var pk=pdfh(it,'.name:eq(2)&&Text');var img=pd(it,'img&&src');var timer=pdfh(it,'.lab_time&&Text');var url=pd(it,'a:eq(1)&&href');items.push({desc:timer+'  '+ps,title:pz+'🆚'+pk,pic_url:img,url:url})});setResult(items);",
    二级:{
	      title:".item.active li:gt(1):lt(5)&&Text;.sub_list li:eq(0)&&Text",//类型 时间
          img:"img&&src",
	      desc:";;;.lab_team_home&&Text;.lab_team_away&&Text",  //演员;导演
	      content:".sub_list ul&&Text",  // 主要信息
	      tabs:"js:TABS=['【直播源】']",
	      lists:"js:LISTS=[];pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;let html=request(input);let data=pdfa(html,'.sub_playlist:eq(#id)&&a');TABS.forEach(function(tab){let d=data.map(function(it){let name=pdfh(it,'strong&&Text');let url=pd(it,'a&&data-play');return name+'$'+url});LISTS.push(d)});"
         },
   搜索:'',
}