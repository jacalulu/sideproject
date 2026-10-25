// Plays the REAL game code: at each move a greedy bot searches lines and loops, scores them against
// the goals, plays the best; animations are skipped. Usage: node bot.js HTML FROM TO RUNS
const { chromium } = require('playwright');
const [html, from, to, runs] = [process.argv[2], +process.argv[3], +process.argv[4], +process.argv[5]];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto('file://' + html); await p.waitForTimeout(2500);
  await p.evaluate(() => { document.getElementById('playBtn').closest('.overlay').classList.add('hidden');
    for (const k of ["seenMorgana","seenSand","seenAnchor","seenCrate","seenOyster","seenJelly"]) localStorage.setItem("mermaidDots."+k,"1"); });
  const res = await p.evaluate(([from, to, runs, UNL]) => {
    const settle = () => { let g = 0; while (state === "fall" && g++ < 60){ for (const row of grid) for (const d of row) if (d){ d.yOff = 0; d.vy = 0; } afterSettle(); } };
    const score = (cells, loop) => {
      const t0 = grid[cells[0].r][cells[0].c].type;
      const need = {}; for (const g of goals) if (g.left > 0) need[g.type.key] = g.left;
      let cl = [];
      if (loop){ for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) if (isFriend(grid[r][c]) && grid[r][c].type === t0) cl.push({ r, c }); }
      else cl = cells;
      let sc = 0; const k = t0.key;
      const useful = Math.min(cl.filter(q => !grid[q.r][q.c].trapped).length, need[k] || 0);
      sc += useful * 3 + cl.length * 0.25;
      const hit = new Set();
      for (const q of cl){
        if (need.sand) for (const [dr, dc] of [[0,0],[1,0],[-1,0],[0,1],[0,-1]]){ const rr = q.r + dr, cc = q.c + dc;
          if (rr >= 0 && rr < ROWS && cc >= 0 && cc < COLS && sand[rr][cc] && !hit.has("s" + rr + "," + cc)){ hit.add("s" + rr + "," + cc); sc += 2.2; } }
        if (grid[q.r][q.c].bomb) sc += 5;
        for (const [dr, dc] of [[1,0],[-1,0],[0,1],[0,-1]]){
          const rr = q.r + dr, cc = q.c + dc;
          if (rr < 0 || rr >= ROWS || cc < 0 || cc >= COLS) continue;
          const d = grid[rr][cc];
          if (d && (d.kind === "crate" || d.kind === "oyster") && need[d.kind] && !hit.has(rr + "," + cc)){ hit.add(rr + "," + cc); sc += 2.6; }
        }
        if (need.anchor) for (let r = 0; r < q.r; r++) if (grid[r][q.c] && grid[r][q.c].kind === "anchor") sc += 1.6 + q.r * 0.15;
      }
      if (levelCfg.bombs && !loop && cells.length >= 6) sc += 2;
      return sc;
    };
    const pick = () => {
      let best = null;
      for (const sq of findSquares()){
        const cells = sq.cells, s = score(cells, true) + 1;
        if (!best || s > best.s) best = { s, cells: [...cells, cells[0]], loop: true };
      }
      for (let r0 = 0; r0 < ROWS; r0++) for (let c0 = 0; c0 < COLS; c0++){
        const d0 = grid[r0][c0]; if (!isFriend(d0)) continue;
        let budget = 500;            // per starting cell, so every part of the board gets searched
        const stack = [[{ r: r0, c: c0 }]];
        while (stack.length && budget-- > 0){
          const pth = stack.pop();
          if (pth.length >= 2){ const s = score(pth, false); if (!best || s > best.s) best = { s, cells: pth, loop: false }; }
          if (pth.length >= 8) continue;
          const l = pth[pth.length - 1];
          for (const [dr, dc] of [[1,0],[-1,0],[0,1],[0,-1]]){
            const rr = l.r + dr, cc = l.c + dc;
            if (rr < 0 || rr >= ROWS || cc < 0 || cc >= COLS) continue;
            const q = grid[rr][cc];
            if (!isFriend(q) || q.type !== d0.type || pth.some(x => x.r === rr && x.c === cc)) continue;
            stack.push([...pth, { r: rr, c: cc }]);
          }
        }
      }
      return best;
    };
    const out = [];
    for (let L = from; L <= to; L++){
      let wins = 0, left = 0, played = 0; const why = {};
      for (let k = 0; k < runs; k++){
        level = L; progress = Math.max(progress, L); startLevel(); settle(); if (UNL) moves = 999;
        let guard = 0;
        while (state === "idle" && guard++ < 80){
          const m = pick(); if (!m){ why.nomove = (why.nomove || 0) + 1; break; }
          path = m.cells; loopClosed = m.loop; clearPath(); settle();
        }
        played++;
        if (state === "idle" && guard >= 80) why.cap = (why.cap || 0) + 1;
        if (state !== "idle" && state !== "over") why["state_" + state] = (why["state_" + state] || 0) + 1;
        if (goals.every(g => g.left <= 0)){ wins++; left += UNL ? 999 - moves : moves; }
        for (const id of ["winOverlay","loseOverlay","storyOverlay","factOverlay"]) document.getElementById(id).classList.add("hidden");
      }
      const c = levelConfig(L);
      out.push({ L, wins, runs: played, avgLeft: wins ? +(left / wins).toFixed(1) : null, moves: c.moves, why,
                 mech: ["sand","anchor","crate","oyster"].filter(x => c[x]).map(x => x + ":" + c[x]).join(" ") + (c.bombs ? " +jelly" : "") });
    }
    return out;
  }, [from, to, runs, !!process.env.UNL]);
  for (const r of res) console.log(JSON.stringify(r));
  console.log("errors:", errs.length ? errs.slice(0, 5) : "none");
  await b.close();
})();
