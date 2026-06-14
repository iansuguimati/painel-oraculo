
function $(i){return document.getElementById(i);}
function getJSON(f){var t=Date.now();return fetch(f+"?t="+t,{cache:"no-store"}).then(function(r){if(!r.ok)throw 0;return r.json();}).catch(function(){return fetch("https://raw.githubusercontent.com/iansuguimati/painel-oraculo/main/"+f+"?t="+t,{cache:"no-store"}).then(function(r){return r.json();});});}
try{
function tk(){var e=$("clk");if(e)e.textContent=new Date().toLocaleTimeString("pt-BR");} tk();setInterval(tk,1000);
function money(v){return (v>0?"+":"")+"R$ "+v;}
function loadStats(){getJSON("stats.json").then(function(s){
  $("mTips").textContent=s.tips;$("mHit").textContent=s.hit;$("mClv").textContent=s.clv;$("mBolao").textContent=s.bolao;$("mRoi").textContent=s.roi;
  /*proximo jogo vem da agenda.json*/
  if(s.analises&&s.analises.length){$("palpitesDia").innerHTML=s.analises.map(function(a){var dc=(!a.disc||a.disc==="-")?"sem tip (sem edge)":a.disc;return '<div style="margin-bottom:16px"><div style="font-size:13px;font-weight:700;color:var(--gold);margin:0 0 8px 2px">'+(a.hora?a.hora+" - ":"")+a.jogo+'</div><div style="font-size:12px;color:var(--mut);margin:0 0 8px 2px">Forca de elenco (talento individual): <b style="color:var(--gold)">'+(a.elenco||"-")+'</b></div><div class="picks"><div class="pick main"><div class="pl">Bolao</div><div class="pv" style="font-size:16px">'+a.bolao+'</div></div><div class="pick"><div class="pl">Disciplinado</div><div class="pv" style="font-size:14px">'+dc+'</div></div><div class="pick"><div class="pl">Jogo Louco</div><div class="pv" style="font-size:14px">'+a.louco+'</div></div><div class="pick"><div class="pl">Favorito Modelo</div><div class="pv" style="font-size:15px;color:var(--green)">'+(a.fav||"-")+'</div><div style="font-size:10px;color:var(--mut);margin-top:2px">@ '+(a.fav_odd||"-")+'</div></div><div class="pick"><div class="pl">Favorito Mercado</div><div class="pv" style="font-size:15px;color:#7fb0e6">'+(a.fav_mkt||"-")+'</div><div style="font-size:10px;color:var(--mut);margin-top:2px">@ '+(a.fav_mkt_odd||"-")+'</div></div></div></div>';}).join("");}
  if(s.analises&&s.analises.length){$("analiseBox").innerHTML=s.analises.map(function(a){return '<div class="acard"><h4>'+a.jogo+'</h4><div class="meta">Bolao: '+a.bolao+'  |  Produto: '+a.disc+'  |  Lab: '+a.louco+'</div><div class="body">'+a.texto+'</div></div>';}).join("");}
  else if(s.analise)$("analiseBox").textContent=s.analise;
  if(s.telegram)$("ctaBtn").href=s.telegram;
  var d=s.sim100.disc,l=s.sim100.louco;
  $("simDisc").textContent=money(d.pnl);$("simDisc").className="big "+(d.pnl>=0?"pos":"neg");$("simDiscSm").textContent="apostado: R$ "+d.stake+" | de volta: R$ "+(d.stake+d.pnl)+" | lucro: R$ "+d.pnl+" | ROI: "+d.roi;
  $("simLouco").textContent=money(l.pnl);$("simLouco").className="big "+(l.pnl>=0?"pos":"neg");$("simLoucoSm").textContent="apostado: R$ "+l.stake+" | de volta: R$ "+(l.stake+l.pnl)+" | lucro: R$ "+l.pnl+" | ROI: "+l.roi;
  if(s.sim100.fav){var fv=s.sim100.fav;$("simFav").textContent=money(fv.pnl);$("simFav").className="big "+(fv.pnl>=0?"pos":"neg");$("simFavSm").textContent="apostado: R$ "+fv.stake+" | de volta: R$ "+(fv.stake+fv.pnl)+" | lucro: R$ "+fv.pnl+" | ROI: "+fv.roi;}
  if(s.sim100.favmkt){var fm=s.sim100.favmkt;$("simFavMkt").textContent=money(fm.pnl);$("simFavMkt").className="big "+(fm.pnl>=0?"pos":"neg");$("simFavMktSm").textContent="apostado: R$ "+fm.stake+" | de volta: R$ "+(fm.stake+fm.pnl)+" | lucro: R$ "+fm.pnl+" | ROI: "+fm.roi;}
  if(s.alerta&&s.alerta.ativo){var ab=$("alertaBox");if(ab){ab.style.display="block";ab.innerHTML='<div class="alertaBanner"><span class="alertaTag">Alerta</span>'+s.alerta.texto+(s.alerta.hora?' <span style="opacity:.7">('+s.alerta.hora+')</span>':'')+'</div>';}}else{var ab0=$("alertaBox");if(ab0)ab0.style.display="none";}
  if(s.odds_fech&&s.odds_fech.jogo){var of=s.odds_fech,ofb=$("oddsFechBox");if(ofb){ofb.style.display="block";ofb.innerHTML='<div class="oddsfech"><span class="oddsfech-t">Odds de fechamento (no apito):</span> <b>'+of.jogo+'</b> &nbsp; 1 <b>'+(of.o1||"-")+'</b> | X <b>'+(of.ox||"-")+'</b> | 2 <b>'+(of.o2||"-")+'</b>'+(of.under?' | U2,5 <b>'+of.under+'</b>':'')+' <span class="oddsfech-n">(base do CLV)</span></div>';}}else{var ofb0=$("oddsFechBox");if(ofb0)ofb0.style.display="none";}
}).catch(function(){});}
function bd(t){var m={analise:["t-analise","Analise"],lance:["t-lance","Lance"],gol:["t-lance","GOL"],ao_vivo:["t-lance","Ao vivo"],fim:["t-previsao","Fim"],clima:["t-previsao","Clima"],esquenta:["t-analise","Esquenta"],forma:["t-analise","Forma"],historico:["t-analise","Historico"],previsao:["t-previsao","Previsao"],alerta:["t-alerta","ALERTA"],odds:["t-odds","Odds"]};return m[t]||["t-lance","Ao vivo"];}
function _norm(s){return (s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");}
function _keys(j){return j.split(" x ").map(function(t){return _norm(t).split(/[-\s]/)[0];});}
function _gameOf(txt){var t=_norm(txt),G=window.GAMES||[];for(var i=0;i<G.length;i++){var k=_keys(G[i].jogo);if(k.length>1&&t.indexOf(k[0])>=0&&t.indexOf(k[1])>=0)return G[i].jogo;}return null;}
var lastTop="";
function loadNews(){getJSON("noticias.json").then(function(d){
  function row(n,cls){var b=bd(n.tipo),h=n.hora||"";return '<div class="ni'+(cls?" "+cls:"")+'"><span class="h">'+h+'</span><span class="tag '+b[0]+'">'+b[1]+'</span><span>'+n.texto+'</span></div>';}
  var changed=d.length&&d[0].texto!==lastTop;if(d.length)lastTop=d[0].texto;
  var html="";
  try{
  var vis=d.slice(0,5),old=d.slice(5);
  if(window.GAMES&&window.GAMES.length){
    var groups=[],idx={};
    vis.forEach(function(n){var g=_gameOf(n.texto)||"Outras atualizacoes";if(!(g in idx)){idx[g]=groups.length;groups.push({jogo:g,items:[]});}groups[idx[g]].items.push(n);});
    html=groups.map(function(gr,gi){
      var inner=gr.items.map(function(n,k){return row(n,(gi===0&&k===0&&changed)?"new":"");}).join("");
      return '<div class="gameGroup"><div class="gameGroupH">'+gr.jogo+'<span class="gg-n">'+gr.items.length+' atualizacoes</span></div>'+inner+'</div>';
    }).join("");
  }else{
    html=vis.map(function(n,k){return row(n,(k===0&&changed)?"new":"");}).join("");
  }
  if(old.length){html+='<div id="oldNews" style="display:none">'+old.map(function(n){return row(n,"");}).join("")+'</div><div style="text-align:center;margin-top:10px"><button id="oldBtn" class="oldbtn" onclick="toggleOld()">Ver anteriores ('+old.length+')</button></div>';}
  }catch(_e){html="";}
  if(!html&&d&&d.length){html=d.slice(0,5).map(function(n,k){return row(n,(k===0&&changed)?"new":"");}).join("");}
  var el=$("newsList");if(el&&html)el.innerHTML=html;var u=$("newsUpd");if(u)u.textContent="atualizado "+new Date().toLocaleTimeString("pt-BR");
}).catch(function(){});}
window.toggleOld=function(){var o=$("oldNews"),b=$("oldBtn");if(!o||!b)return;if(o.style.display==="none"){o.style.display="block";b.textContent="Ver menos";}else{o.style.display="none";b.textContent="Ver anteriores ("+o.children.length+")";}};
function loadAgenda(){getJSON("agenda.json").then(function(d){window.GAMES=d;try{loadNews();}catch(_e){}
  var h=d.map(function(g){var tg=(g.palpite&&g.palpite!=="-")?'<span class="tag t-previsao">'+g.palpite+'</span>':'<span class="tag t-lance">agendado</span>';
  return '<div class="ni"><span class="h">'+g.data+' '+g.hora+'</span>'+tg+'<span>'+g.jogo+(g.grupo&&g.grupo!=="-"?' (Grupo '+g.grupo+')':'')+'</span></div>';}).join("");
  try{var now=new Date(),yr=now.getFullYear(),prox=null;for(var z=0;z<d.length;z++){var pp=d[z].data.split("/"),hm=(d[z].hora||"00:00").split(":"),dt=new Date(yr,parseInt(pp[1],10)-1,parseInt(pp[0],10),parseInt(hm[0],10),parseInt(hm[1],10));if(dt.getTime()>now.getTime()){prox=d[z];break;}}if(prox){var nj=$("nextJogo"),nh=$("nextHora");if(nj)nj.textContent=prox.jogo;if(nh)nh.textContent=prox.hora+" (Brasilia)";}}catch(e){}
  var el=$("agendaList");if(el&&h)el.innerHTML=h;
}).catch(function(){});}
function loadCharts(){if(!window.Chart)return;getJSON("historico.json").then(function(H){
  (function(){var pnl=function(v){if(v==null)return '<td>-</td>';var c=v>0?"pos":(v<0?"neg":"");return '<td class="'+c+'">'+(v>0?"+":"")+v+'</td>';};
  var rows=H.slice().reverse().map(function(g){return '<tr><td>'+g.data+'</td><td>'+g.jogo+'</td><td>'+(g.venc?'<span class="pos">OK</span>':'<span class="neg">X</span>')+'</td><td>'+(g.placar?'<span class="pos">OK</span>':'<span class="neg">X</span>')+'</td><td>'+g.bolao_pts+'</td><td>'+((g.brier_k!=null?g.brier_k.toFixed(2):'-')+' / '+(g.brier_m!=null?g.brier_m.toFixed(2):'-'))+'</td>'+pnl(g.fav)+pnl(g.disc)+pnl(g.louco)+pnl(g.favmkt)+'</tr>';}).join("");
  var t='<table class="trk"><thead><tr><th>Data</th><th>Jogo</th><th>Venc</th><th>Placar</th><th>Pts</th><th>Brier k/m</th><th>Fav</th><th>Disc</th><th>Louco</th><th>Mkt</th></tr></thead><tbody>'+rows+'</tbody></table>';
  var te=$("trkTable");if(te)te.innerHTML=t;})();
  var labels=H.map(function(g){return g.jogo;});
  function cum(k){var t=0;return H.map(function(g){t+=g[k];return t;});}
  var gc="rgba(255,255,255,.07)",tc="#9fb3c8";
  var base={responsive:true,plugins:{legend:{labels:{color:tc,boxWidth:12,font:{size:11}}}},scales:{x:{ticks:{color:tc,font:{size:10}},grid:{color:gc}},y:{ticks:{color:tc,font:{size:10}},grid:{color:gc}}}};
  new Chart(document.getElementById("cLucro"),{type:"line",data:{labels:labels,datasets:[
    {label:"Favorito do Modelo",data:cum("fav"),borderColor:"#3fb98a",backgroundColor:"#3fb98a",tension:.2},
    {label:"Disciplinado",data:cum("disc"),borderColor:"#C8A24B",backgroundColor:"#C8A24B",tension:.2},
    {label:"Jogo Louco",data:cum("louco"),borderColor:"#e06464",backgroundColor:"#e06464",tension:.2},{label:"Favorito do Mercado",data:cum("favmkt"),borderColor:"#7fb0e6",backgroundColor:"#7fb0e6",tension:.2}]},options:base});
  var vp=[],pp=[],sv=0,sp=0;H.forEach(function(g,i){sv+=g.venc;sp+=g.placar;vp.push(Math.round(sv/(i+1)*100));pp.push(Math.round(sp/(i+1)*100));});
  var o2=JSON.parse(JSON.stringify(base));o2.scales.y.min=0;o2.scales.y.max=100;
  new Chart(document.getElementById("cAcerto"),{type:"line",data:{labels:labels,datasets:[
    {label:"% vencedor",data:vp,borderColor:"#3fb98a",backgroundColor:"#3fb98a",tension:.2},
    {label:"% placar exato",data:pp,borderColor:"#C8A24B",backgroundColor:"#C8A24B",tension:.2}]},options:o2});
  var bm=[],bk=[],tm=0,tk=0;H.forEach(function(g,i){tm+=g.brier_m;tk+=g.brier_k;bm.push((tm/(i+1)).toFixed(3));bk.push((tk/(i+1)).toFixed(3));});
  new Chart(document.getElementById("cBrier"),{type:"line",data:{labels:labels,datasets:[
    {label:"Modelo",data:bm,borderColor:"#C8A24B",backgroundColor:"#C8A24B",tension:.2},
    {label:"Mercado",data:bk,borderColor:"#7fb0e6",backgroundColor:"#7fb0e6",tension:.2}]},options:base});
}).catch(function(){});}
loadStats();loadNews();loadAgenda();loadCharts();setInterval(loadStats,20000);setInterval(loadNews,20000);setInterval(loadAgenda,120000);
}catch(e){}
