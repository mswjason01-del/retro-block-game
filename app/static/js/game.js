(() => {
  const boardCanvas = document.querySelector('#board');
  if (!boardCanvas) return;
  const ctx = boardCanvas.getContext('2d'), nextCtx = document.querySelector('#next').getContext('2d');
  const COLS=10, ROWS=20, CELL=30;
  const colors={I:'#00e5ff',O:'#ffe066',T:'#b566ff',S:'#49e365',Z:'#ff5a72',J:'#4d7cff',L:'#ff9f43'};
  const shapes={I:[[1,1,1,1]],O:[[1,1],[1,1]],T:[[0,1,0],[1,1,1]],S:[[0,1,1],[1,1,0]],Z:[[1,1,0],[0,1,1]],J:[[1,0,0],[1,1,1]],L:[[0,0,1],[1,1,1]]};
  let grid, piece, next, bag=[], score=0, lines=0, level=1, sessionId=null, running=false, paused=false, last=0, dropAt=0;
  const $=id=>document.querySelector(id), overlay=$('#overlay');
  const fmt=n=>Number(n).toLocaleString();
  function newGrid(){ return Array.from({length:ROWS},()=>Array(COLS).fill(null)); }
  function refill(){ bag=Object.keys(shapes).sort(()=>Math.random()-.5); }
  function make(type){ if(!type){if(!bag.length) refill();type=bag.pop();} return {type,shape:shapes[type].map(r=>[...r]),x:Math.floor((COLS-shapes[type][0].length)/2),y:0}; }
  function collides(p, dx=0,dy=0,shape=p.shape){return shape.some((row,y)=>row.some((v,x)=>v && (x+p.x+dx<0||x+p.x+dx>=COLS||y+p.y+dy>=ROWS||(y+p.y+dy>=0&&grid[y+p.y+dy][x+p.x+dx]))));}
  function rotate(shape){return shape[0].map((_,i)=>shape.map(row=>row[i]).reverse());}
  function move(dx,dy){if(!running||paused)return false;if(!collides(piece,dx,dy)){piece.x+=dx;piece.y+=dy;draw();return true}if(dy){lock()}return false}
  function turn(){if(!running||paused)return;const r=rotate(piece.shape);for(const kick of [0,-1,1,-2,2])if(!collides(piece,kick,0,r)){piece.shape=r;piece.x+=kick;draw();break}}
  function hardDrop(){if(!running||paused)return;let distance=0;while(!collides(piece,0,1)){piece.y++;distance++}score+=distance*2;lock();}
  function lock(){piece.shape.forEach((row,y)=>row.forEach((v,x)=>{if(v&&piece.y+y>=0)grid[piece.y+y][piece.x+x]=piece.type;}));let cleared=0;grid=grid.filter(row=>{if(row.every(Boolean)){cleared++;return false}return true});while(grid.length<ROWS)grid.unshift(Array(COLS).fill(null));if(cleared){score+=([0,100,300,500,800][cleared]||0)*level;lines+=cleared;level=1+Math.floor(lines/10);}piece=next;next=make();if(collides(piece)){endGame()} update();draw();}
  function update(){$('#score').textContent=fmt(score);$('#lines').textContent=lines;$('#level').textContent=level;}
  function block(context,x,y,color,size=CELL){context.fillStyle=color;context.fillRect(x*size,y*size,size,size);context.fillStyle='#ffffff33';context.fillRect(x*size+2,y*size+2,size-4,3);context.strokeStyle='#00000088';context.strokeRect(x*size+.5,y*size+.5,size-1,size-1);}
  function draw(){ctx.fillStyle='#090a11';ctx.fillRect(0,0,300,600);ctx.strokeStyle='#ffffff12';for(let i=1;i<COLS;i++){ctx.beginPath();ctx.moveTo(i*CELL,0);ctx.lineTo(i*CELL,600);ctx.stroke()}for(let i=1;i<ROWS;i++){ctx.beginPath();ctx.moveTo(0,i*CELL);ctx.lineTo(300,i*CELL);ctx.stroke()}grid.forEach((row,y)=>row.forEach((v,x)=>v&&block(ctx,x,y,colors[v])));if(piece)piece.shape.forEach((row,y)=>row.forEach((v,x)=>v&&block(ctx,piece.x+x,piece.y+y,colors[piece.type])));drawNext();}
  function drawNext(){nextCtx.clearRect(0,0,120,120);if(!next)return;const size=24,w=next.shape[0].length*size,h=next.shape.length*size;next.shape.forEach((row,y)=>row.forEach((v,x)=>v&&block(nextCtx,(x*size+60-w/2)/size,(y*size+60-h/2)/size,colors[next.type],size)));}
  async function start(){grid=newGrid();refill();next=make();piece=make();score=lines=0;level=1;running=true;paused=false;last=dropAt=performance.now();update();overlay.classList.add('hidden');$('#pause').textContent='PAUSE';draw();try{const r=await fetch('/api/game/start',{method:'POST',headers:{'X-CSRF-Token':document.querySelector('.game-shell').dataset.csrf}});sessionId=(await r.json()).session_id;}catch(e){sessionId=null;}requestAnimationFrame(loop);}
  function loop(t){if(!running)return;if(!paused&&t-dropAt>Math.max(110,800-(level-1)*65)){move(0,1);dropAt=t;}requestAnimationFrame(loop);}
  async function endGame(){running=false;let message=`SCORE ${fmt(score)}<br>HIGH SCORE ${$('#high-score').textContent}`;if(sessionId){try{const r=await fetch('/api/game/finish',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':document.querySelector('.game-shell').dataset.csrf},body:JSON.stringify({session_id:sessionId,score,lines,level})});const result=await r.json();if(result.saved){$('#high-score').textContent=fmt(result.high_score);message=`SCORE ${fmt(score)}<br>HIGH SCORE ${fmt(result.high_score)}${result.new_high_score?'<br><br>🎉 NEW HIGH SCORE!':''}${result.new_global_record?'<br>🏆 NEW #1 SCORE!':''}`;}}catch(e){message+='';}}overlay.innerHTML=`<h2>GAME OVER</h2><p>${message}</p><button id="start" class="button primary">PLAY AGAIN</button><a class="button" href="/leaderboard">LEADERBOARD</a>`;overlay.classList.remove('hidden');$('#start').addEventListener('click',start);}
  function pause(){if(!running)return;paused=!paused;$('#pause').textContent=paused?'RESUME':'PAUSE';if(paused){overlay.innerHTML='<h2>PAUSED</h2><p>PRESS P OR TAP RESUME</p>';overlay.classList.remove('hidden')}else overlay.classList.add('hidden');}
  document.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowDown','ArrowUp',' '].includes(e.key))e.preventDefault();if(e.key==='ArrowLeft')move(-1,0);if(e.key==='ArrowRight')move(1,0);if(e.key==='ArrowDown'){if(move(0,1))score++;update();}if(e.key==='ArrowUp')turn();if(e.key===' ')hardDrop();if(e.key.toLowerCase()==='p'||e.key==='Escape')pause();});
  document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('pointerdown',e=>{e.preventDefault();({left:()=>move(-1,0),right:()=>move(1,0),down:()=>{if(move(0,1)){score++;update()}},rotate:turn,drop:hardDrop})[b.dataset.action]();}));
  $('#start').addEventListener('click',start);$('#pause').addEventListener('click',pause);$('#fullscreen').addEventListener('click',()=>document.querySelector('.game-shell').requestFullscreen?.());
  grid=newGrid();next=make('T');piece=make('O');draw();
})();
