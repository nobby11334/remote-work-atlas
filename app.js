const prefectures='北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県'.split(' ');
const select=document.getElementById('pref-select');
if(select){for(const name of prefectures){const op=document.createElement('option');op.value=name;op.textContent=name;select.appendChild(op)}/* 都道府県別表示は統計JSONの読み込み完了後に設定 */}
const pct=x=>x.toFixed(1);const delta=(a,b)=>(a-b).toFixed(1);const byId=(d,id)=>d.indicators.find(x=>x.id===id);function setTxt(id,value){const el=document.getElementById(id);if(el)el.textContent=value;}
function insight(d){const p=byId(d,'persol_usage'),w=byId(d,'persol_wish'),o=byId(d,'persol_office'),tok=byId(d,'persol_tokyo'),all=byId(d,'mlit_last_year');const dPersol=delta(p.value,p.prior_value),dMlit=delta(all.value,all.prior_value),gap=delta(tok.value,p.value);const rows=[{tag:'最新の調査から',headline:'実施率は低下、継続意向は高水準',text:`パーソル総合研究所の${p.year}年調査では、正社員のテレワーク実施率は${pct(p.value)}％で前年から${Math.abs(Number(dPersol)).toFixed(1)}ポイント${Number(dPersol)<0?'低下':'上昇'}しました。一方、実施者の継続希望は${pct(w.value)}％。企業側の原則出社指示は${pct(o.value)}％です。`},{tag:'地域差',headline:'東京と全国平均との差は'+gap+'ポイント',text:`同じ調査で東京都の実施率は${pct(tok.value)}％、全国の正社員は${pct(p.value)}％でした。差は${gap}ポイントですが、これはフルリモート求人の地域差ではありません。`},{tag:'別調査の動向',headline:'国交省の別定義では増加',text:`国土交通省の${all.year}年度調査では「直近1年間の実施率」が${pct(all.value)}％で前年度から${dMlit}ポイント増加しました。調査の定義・対象が違うため、パーソルの${p.year}年調査とは直接比較できません。`}];const root=document.getElementById('analysis-messages');if(root){root.replaceChildren();rows.forEach(r=>{const item=document.createElement('article');item.className='analysis-item';const tag=document.createElement('span');tag.className='overline';tag.textContent=r.tag;const h=document.createElement('h3');h.textContent=r.headline;const text=document.createElement('p');text.textContent=r.text;item.append(tag,h,text);root.append(item)})}
setTxt('metric-usage',pct(p.value));setTxt('metric-office',pct(o.value));setTxt('metric-wish',pct(w.value));setTxt('metric-mlit',pct(all.value));setTxt('metric-diff',dPersol+'pt');setTxt('metric-mlit-diff','+'+dMlit+'pt');setTxt('research-updated',d.updated_at.replaceAll('-','.'));const extra=document.getElementById('extra-metrics');if(extra){extra.replaceChildren();[['persol_it','情報通信業'],['persol_tokyo','東京都'],['persol_kanto','関東'],['persol_frequency_down','テレワーク頻度が減った人'],['mlit_ever','これまでにテレワーク経験あり']].forEach(([id,label])=>{const m=byId(d,id);const el=document.createElement('div');el.className='extra-metric';const b=document.createElement('b');b.textContent=label;const v=document.createElement('strong');v.textContent=pct(m.value)+'%';const note=document.createElement('span');note.textContent=m.source==='persol_2026'?'パーソル 2026年':'国交省 2025年度';el.append(b,v,note);extra.append(el)})}
drawChart([{year:p.prior_year,value:p.prior_value},{year:p.year,value:p.value}], 'パーソル総合研究所・全国正社員');}
function drawChart(series,label){const el=document.getElementById('trend-chart');if(!el)return;el.replaceChildren();const wrap=document.createElement('div');wrap.className='comparison-bars';series.forEach(s=>{const row=document.createElement('div');row.className='comparison-row';const year=document.createElement('span');year.textContent=s.year+'年';const track=document.createElement('div');track.className='comparison-track';const fill=document.createElement('div');fill.className='comparison-fill';fill.style.width=(s.value/35*100)+'%';track.append(fill);const val=document.createElement('strong');val.textContent=pct(s.value)+'%';row.append(year,track,val);wrap.append(row)});const note=document.createElement('p');note.className='footnote';note.textContent=label+'：異なる定義の国交省データをこのグラフには混ぜていません。';el.append(wrap,note)}
async function load(){try{const resp=await fetch('data/indicators.json',{cache:'no-store'});if(!resp.ok)throw Error('HTTP '+resp.status);const data=await resp.json();if(data.schema_version!==2||!Array.isArray(data.indicators))throw Error('invalid schema');insight(data)}catch(e){console.error('統計データ取得に失敗',e);setTxt('analysis-status','統計データを読み込めませんでした。再読み込みをお試しください。');}}
load();

async function loadPrefectures(){
  const result=document.getElementById('pref-result'),board=document.getElementById('pref-ranking');
  if(!select || !result)return;
  try{
    const response=await fetch('data/prefectures_2025.json',{cache:'no-store'});
    if(!response.ok)throw Error('HTTP '+response.status);
    const data=await response.json();
    if(data.prefectures.length!==47)throw Error('incomplete data');
    const list=data.prefectures;
    function show(){
      const name=select.value;
      result.replaceChildren();
      const target=list.find(x=>x.name===name);
      const num=document.createElement('div');num.className='no-data-icon';num.textContent=target?target.rate+'%':'47';
      if(target)num.classList.add('pref-number');
      const h=document.createElement('h4');h.textContent=target?name+'：テレワーク経験率 '+target.rate+'%':'47都道府県のテレワーク経験率を収録';
      const desc=document.createElement('p');desc.textContent=target?'2025年調査。企業等に勤務する人の過去1年の経験率。掲載表の回答者数：'+target.respondents+'人。全国値26.9%との差 '+(target.rate-data.national>=0?'+':'')+(target.rate-data.national).toFixed(1)+'ポイント。':'地域を選ぶと実績値を確認できます。学校卒業生のフルリモート就職数・出社回帰による転居数は、まだ収集できていません。';
      const caveat=document.createElement('p');caveat.className='pref-disclaimer';caveat.textContent='※出典：総務省2025年通信利用動向調査・表35の二次集計。原CSVとの全件突合は未実施。フルリモート求人率ではありません。';
      result.append(num,h,desc,caveat);
    }
    select.addEventListener('change',show);show();
    if(board){
      board.replaceChildren();
      list.forEach((p,i)=>{
        const row=document.createElement('div');row.className='pref-ranking-row';
        const label=document.createElement('span');label.textContent=(i+1)+'. '+p.name;
        const track=document.createElement('div');track.className='pref-ranking-track';
        const fill=document.createElement('span');fill.className='pref-ranking-fill';fill.style.width=(p.rate/50*100)+'%';track.append(fill);
        const val=document.createElement('strong');val.textContent=p.rate+'%';
        row.append(label,track,val);
        row.addEventListener('click',()=>{select.value=p.name;show();result.scrollIntoView({behavior:'smooth',block:'center'})});
        board.append(row);
      });
    }
    const summary=document.getElementById('pref-stat-summary');
    if(summary)summary.textContent='47都道府県を収録。最高 神奈川県45.3％、最低 青森県6.9％、差38.4ポイント。全国26.9％。同一調査の経験率に基づく比較です。';
    const analysis=document.getElementById('analysis-messages');
    if(analysis){
      const item=document.createElement('article');item.className='analysis-item';
      const tag=document.createElement('span');tag.className='overline';tag.textContent='都道府県格差 / 2025年総務省';
      const title=document.createElement('h3');title.textContent='テレワーク経験率には38.4ポイントの地域差';
      const p=document.createElement('p');p.textContent='都道府県別では神奈川県45.3％、青森県6.9％。最大と最小の差は38.4ポイントです。ただし、地域の産業構成や職種などを調整した格差ではなく、フルリモート就職可能性や人口流出の因果関係を示すものではありません。';
      const link=document.createElement('a');link.href=data.primary_source;link.target='_blank';link.rel='noopener noreferrer';link.textContent='総務省の原統計表 ↗';item.append(tag,title,p,link);analysis.append(item);
    }
  }catch(e){console.error('Prefecture data load failed',e);result.textContent='都道府県別データを読み込めませんでした。';}
}
loadPrefectures();
