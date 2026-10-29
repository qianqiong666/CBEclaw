from pathlib import Path
import hashlib, re, sys
root = Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
site = root/'shortfilm/index.html'
source = site.read_bytes()
html = source.decode('utf-8')
if 'id="paid-growth"' in html:
    raise SystemExit('Paid-growth supplement already exists; review instead of appending twice.')
sha = hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()
if sha != 'f84096d1b2c8cdf280e86ab223d68285004845e8':
    raise SystemExit('Source changed: '+sha+'; reconcile before overwrite.')
part = root/'.github/report-parts/paid-growth-20261029/content.html'
addition = part.read_text('utf-8').replace('2026.10.29','2026.10.30')
assert 'id="paid-growth"' in addition and 'id="pgs12"' in addition
addition = addition.replace('本模块只算项目贡献，不自动代表税后利润或本金投资回报。','本模块按内容分销的分账模型计算项目贡献，不自动代表税后利润或本金投资回报；电商使用时须另外计入货品、履约、售后等成本。')
css = '''
/* 2026-10-30 paid-growth supplement; original design retained. */
.pg-results{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;background:#102033;color:#fff;border-radius:14px;padding:22px;margin:18px 0}
.pg-results span{display:block;color:#bdccdc;font-size:12px}.pg-results strong{display:block;font-size:24px;line-height:1.45;margin-top:6px;overflow-wrap:anywhere}
.pg-results strong[data-sign="negative"]{color:#ffc0b2}.pg-results strong[data-sign="positive"]{color:#b6edce}
.pg-section .fields label{line-height:1.7}.pg-section .fields input{font-size:16px;min-width:0}.pg-section .copybox{overflow-wrap:anywhere}
.pg-section .button,.pg-section button{white-space:normal;line-height:1.6}.pg-section .flow{margin-bottom:16px}
.pg-archive{margin-top:42px;padding:18px 22px;border-top:2px solid #cfdbe6;border-bottom:1px solid #dfe6ed;color:#586a7f;font-size:14px}
@media(max-width:760px){.pg-results{grid-template-columns:1fr;gap:15px;padding:19px}.pg-results>div{display:flex;align-items:center;justify-content:space-between;gap:12px}.pg-results span{max-width:50%;font-size:12px}.pg-results strong{font-size:21px;white-space:nowrap;margin:0}.pg-section .fields{grid-template-columns:repeat(2,minmax(0,1fr))}.pg-section .fields label{font-size:11px;min-width:0}.pg-section .fields input{padding:10px 8px}.pg-section .copybox{font-size:12px}.pg-archive{padding:15px 18px}}
@media print{.pg-results{color:#172439;background:#eef3f7;border:1px solid #ccd7e3}.pg-results span{color:#516277}.pg-results strong[data-sign]{color:#172439}.pg-section .buttons{display:none}}
'''
js = r'''
(function(){
 'use strict';
 const defaults={spend:1000000,roas:1.35,share:80,refund:5,cost:30000,target:6,period:30,days:35};
 const money=new Intl.NumberFormat('zh-CN',{maximumFractionDigits:0});
 function input(k){const n=Number(document.getElementById('pg-'+k).value);return Number.isFinite(n)?Math.max(0,n):0;}
 function calculate(){
  const a=input('spend'),g=input('roas'),s=Math.min(100,input('share'))/100,h=Math.min(100,input('refund'))/100,c=input('cost'),t=input('target')/100,period=Math.max(1,input('period')),lag=input('days');
  const net=a*g*s*(1-h),profit=net-a-c,denom=a*s*(1-h);
  const required=denom>0?(a*(1+t)+c)/denom:null,zero=denom>0?(a+c)/denom:null;
  const margin=a>0?profit/a*100:null,capital=a/period*lag;
  document.getElementById('pg-net').textContent='¥'+money.format(net);
  const pe=document.getElementById('pg-profit');pe.textContent=(profit<0?'−¥':'¥')+money.format(Math.abs(profit));pe.dataset.sign=profit<0?'negative':'positive';
  document.getElementById('pg-margin').textContent=margin===null?'—':margin.toFixed(2)+'%';
  document.getElementById('pg-needed').textContent=required===null?'不可计算':required.toFixed(4);
  document.getElementById('pg-zero').textContent=zero===null?'不可计算':zero.toFixed(4);
  document.getElementById('pg-cash').textContent='¥'+money.format(capital);
  document.getElementById('pg-note').textContent=a<=0?'请填写大于0的广告消耗。分账为0或扣回为100%时，没有可达的回本ROAS。':'假设净应得收入＝广告消耗×用户侧毛ROAS×本公司分账×(1−尚未扣除的退款/无效预留)。结果非税后净利润，不含未填入的成本。';
  return {a,g,s,h,c,t,net,profit,margin,required,zero,capital};
 }
 Object.keys(defaults).forEach(k=>document.getElementById('pg-'+k).addEventListener('input',calculate));
 document.getElementById('pg-preset').addEventListener('click',()=>{Object.entries(defaults).forEach(([k,v])=>document.getElementById('pg-'+k).value=v);calculate();});
 document.getElementById('pg-copy').addEventListener('click',()=>{const r=calculate();copy('买量经营测算（假设，非收益承诺）\n广告消耗：'+money.format(r.a)+'元\n用户侧毛ROAS：'+r.g+'\n本公司分账：'+(r.s*100).toFixed(0)+'%\n后续扣回预留：'+(r.h*100).toFixed(0)+'%\n其他成本：'+money.format(r.c)+'元\n净应得：'+money.format(r.net)+'元\n项目贡献：'+money.format(r.profit)+'元\n目标利润/广告消耗：'+(r.t*100).toFixed(1)+'%\n达到目标所需毛ROAS：'+(r.required===null?'不可计算':r.required.toFixed(4))+'\n必须按实际分成基数核算，不重复扣已计费用。');});
 calculate();
})();
'''
# Normalize copy text line breaks while keeping valid JavaScript string escapes.
js = js.replace('\\\\n','\\n')
marker='<section id="decision">'
assert html.count(marker)==1
archive='<div class="pg-archive"><b>原方案资料区：</b>下面保留公司主体、账号、原创招聘、网络与制作计划，原始资料日期见各节。最新买量执行与预算以本页上方2026.10.30补充为准；未全面重查的历史信息不冒称本轮核验。</div>'
html=html.replace(marker,addition+'\n'+archive+'\n'+marker,1)
html=html.replace('</style>',css+'\n</style>',1)
nav='<nav class="nav" aria-label="章节导航">'
assert nav in html
html=html.replace(nav,nav+'<a href="#paid-growth">买量执行</a><a href="#paid-channels">渠道入口</a><a href="#paid-economics">利润测算</a><a href="#paid-pilot">试投预算</a><a href="#paid-system">16技能</a><a href="#paid-outreach">商务清单</a>',1)
html,n=re.subn(r'(<header class="hero">.*?<h1>).*?(</h1>)',lambda m:m.group(1)+'AI内容与短剧买量<br>用自动化降低成本，<br>用真实结算验证利润。'+m.group(2),html,count=1,flags=re.S)
assert n==1
html,n=re.subn(r'(<header class="hero">.*?</h1><p>).*?(</p>)',lambda m:m.group(1)+'国内电商与授权分销先验证，海外优先合作已有片库与商业化承接。保留10账号、50条合格输出目标，但以净贡献、资金周转和增量回报决定是否扩大预算。'+m.group(2),html,count=1,flags=re.S)
assert n==1
html=html.replace('管理层 / 内容 / 财务共读 · 更新2026.10.26','管理层 / 投放 / 财务共读 · 买量补充2026.10.30',1)
html=html.replace('<title>AI短片与海外微短剧｜公司决策与执行方案</title>','<title>AI短剧买量与经营｜公司决策、利润测算与执行</title>',1)
html=html.replace('</body>','<script>\n'+js+'\n</script></body>',1)
summary='买量执行建议：现有电商先验证利润，国内授权分销对接真实任务，海外优先已有片库和商业化承接。TikTok Growth Max与Creator Rewards不同；YouTube买流量应导向真实商业转化，不靠买播放套取奖励。投前确认权利、资产、归因、应得分账和账期。10账号与50条产能是工具配置，放量依据是净贡献与回款。固定报告：https://qianqiong666.github.io/CBEclaw/shortfilm/'
html,n=re.subn(r"document\.getElementById\('copy'\)\.onclick=\(\)=>copy\('.*?'\);document\.getElementById\('share'\)",lambda m:"document.getElementById('copy').onclick=()=>copy('"+summary+"');document.getElementById('share')",html,count=1,flags=re.S)
assert n==1
html=html.replace('公开决策阅读版，不含个人报酬、客户秘密或账号密钥。','最新补充：2026.10.30 · 买量渠道、净收益测算与分批试投。<br>公开决策阅读版，不含个人报酬、客户秘密或账号密钥。',1)
ids=re.findall(r'\bid="([^"]+)"',html)
assert len(ids)==len(set(ids)), 'Duplicate IDs'
for anchor in re.findall(r'href="#([^"]+)"',html):
    assert anchor in ids, 'Broken anchor: '+anchor
assert html.count('id="paid-growth"')==1
assert '不要求Python、前后端或App开发' in html
assert '5 YouTube + 5 TikTok' in html
site.write_text(html,encoding='utf-8')
print('Updated',site,len(html),'characters')
