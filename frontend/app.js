
(async function () {
  // ---------- CONFIG & DATA ----------
  let CONFIG = { apiBase: '' };
  try {
    const r = await fetch('config.json');
    if (r.ok) CONFIG = await r.json();
  } catch (e) { console.warn('config.json not loaded', e); }
  const API_BASE = (CONFIG.apiBase || '').replace(/\/$/, '');

  let EXPLOITS = [];
  try {
    const xr = await fetch('exploits.json');
    if (xr.ok) EXPLOITS = await xr.json();
  } catch (e) { console.warn('exploits.json not loaded', e); }

  const apiUrl = (path) => (API_BASE ? API_BASE + path : path);

  // ---------- GLOBAL MODE TOGGLE ----------
  const STORAGE_KEY = 'cmf_mode';
  let globalMode = localStorage.getItem(STORAGE_KEY) || 'simulate';

  function setGlobalMode(mode) {
    globalMode = (mode === 'real') ? 'real' : 'simulate';
    localStorage.setItem(STORAGE_KEY, globalMode);

    const btn = document.getElementById('global-mode-toggle');
    if (btn) btn.textContent = (globalMode === 'simulate' ? 'Mode: Simulate' : 'Mode: Real');

    // propagate to pages
    const modeSelect = document.getElementById('mode');
    if (modeSelect) modeSelect.value = globalMode;

    const psSim = document.getElementById('ps-simulate');
    const httpSim = document.getElementById('http-simulate');
    const pingSim = document.getElementById('ping-simulate');
    if (psSim) psSim.checked = (globalMode === 'simulate');
    if (httpSim) httpSim.checked = (globalMode === 'simulate');
    if (pingSim) pingSim.checked = (globalMode === 'simulate');
  }

  function ensureHeaderToggle() {
    const nav = document.querySelector('header nav');
    if (!nav) return;
    if (document.getElementById('global-mode-toggle')) return;
    const btn = document.createElement('button');
    btn.id = 'global-mode-toggle';
    btn.className = 'btn ghost small';
    btn.style.marginLeft = '8px';
    btn.addEventListener('click', () => setGlobalMode(globalMode === 'simulate' ? 'real' : 'simulate'));
    nav.appendChild(btn);
    setGlobalMode(globalMode);
  }

  // Put the toggle in place as early as possible
  ensureHeaderToggle();

  // ---------- UTILITIES ----------
  function rnd(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
  function nowTs() { return new Date().toISOString().replace('T', ' ').split('.')[0]; }

  // ---------- SIMULATION HELPERS ----------
  const PORT_SERVICES = {
    21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'domain', 80: 'http', 110: 'pop3',
    139: 'netbios-ssn', 143: 'imap', 443: 'https', 445: 'microsoft-ds', 3306: 'mysql',
    8080: 'http-proxy', 8443: 'https-alt'
  };

  function simulatePortScan(rhost, startPort, endPort) {
    const lines = [];
    lines.push(`Starting Nmap 7.91 ( https://nmap.org ) at ${nowTs()}`);
    lines.push(`Nmap scan report for ${rhost}`);
    lines.push(`Host is up (0.${rnd(5,70)}0s latency).`);
    lines.push(`PORT     STATE    SERVICE`);
    const ports = [];
    for (let p = Math.max(1, startPort); p <= Math.min(65535, endPort); p++) {
      if (ports.length >= 40) break;
      if (Math.random() < 0.12 || PORT_SERVICES[p]) { ports.push(p); }
      else if (Math.random() < 0.02) { ports.push(p); }
    }
    [22, 80, 443, 21, 445, 3306].forEach(p => {
      if (p >= startPort && p <= endPort && !ports.includes(p)) ports.push(p);
    });
    ports.sort((a, b) => a - b);
    ports.forEach(p => {
      const svc = PORT_SERVICES[p] || (Math.random() < 0.6 ? 'tcp-' + p : 'unknown');
      const state = (Math.random() < (svc === 'unknown' ? 0.12 : 0.4)) ? 'open' : 'closed';
      lines.push(`${p.toString().padEnd(8)} ${state.padEnd(8)} ${svc}`);
    });
    lines.push('');
    lines.push(`Nmap done: 1 IP address (1 host up) scanned in ${rnd(1,20)}.0 seconds`);
    return lines.join('\n');
  }

  function simulateHttpCheck(url) {
    const servers = ['Apache/2.4.41 (Ubuntu)', 'nginx/1.18.0', 'lighttpd/1.4.55', 'Microsoft-IIS/10.0', 'gunicorn/20.0.4'];
    const statuses = [200, 200, 301, 403, 404, 500];
    const st = pick(statuses);
    const server = pick(servers);
    const respTime = `0.${rnd(10,400)}s`;
    const lines = [];
    lines.push(`HTTP/${st} ${st === 200 ? 'OK' : (st === 301 ? 'Moved Permanently' : st === 403 ? 'Forbidden' : st === 404 ? 'Not Found' : 'Server Error')}`);
    lines.push(`Server: ${server}`);
    lines.push(`Date: ${nowTs()}`);
    lines.push(`Content-Type: text/html; charset=UTF-8`);
    lines.push('');
    lines.push(`<html><head><title>${st === 200 ? 'Welcome' : 'Error ' + st}</title></head><body>`);
    lines.push(`<h1>${st === 200 ? 'Hello' : 'Error ' + st}</h1>`);
    lines.push(`<!-- simulated response, ${respTime} -->`);
    lines.push(`</body></html>`);
    return lines.join('\n');
  }

  function simulatePing(rhost) {
    return `PING ${rhost} (${rhost}) 56(84) bytes of data.\n64 bytes from ${rhost}: icmp_seq=1 ttl=64 time=0.${rnd(5,120)} ms\n--- ${rhost} ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time ${rnd(10,30)}ms`;
  }

  // ---------- RANDOMIZED SIMULATE TEMPLATES ----------
  // Each key = exploit id (matches exploits.json "id"). Each value = array of templates.
  const SIM_TEMPLATES = {
    "smb-ms17-010": [
      "[*] Using exploit module: exploit/windows/smb/ms17_010_eternalblue\n[*] RHOST => {rhost}\n[*] RPORT => {rport}\n[*] Using payload: {payload}\n[*] Sending stage (0.0{n}s)\n[+] Meterpreter session 1 opened ({lhost}:{lport} -> {rhost}:50000) at {now}\n[+] Exploit completed successfully",
      "[*] Module started against {rhost}:{rport}\n[-] Unexpected target response during heap spray\n[-] Exploit unsuccessful: target not vulnerable\n[*] Session closed at {now}"
    ],
    "unix-ftp-proftpd": [
      "[*] Using exploit module: exploit/unix/ftp/proftpd_modcopy_exec\n[*] RHOST => {rhost}\n[*] RPORT => {rport}\n[*] Executing payload...\n[+] Command shell opened on {rhost}:42123\n[+] Post-exploitation: simple ls / - succeeded\n[*] Completed at {now}",
      "[*] Attempting copy trick on {rhost}\n[-] Connection reset by peer\n[-] Exploit failed: service terminated unexpectedly\n[*] Finished at {now}"
    ],
    "reverse-shell-tcp": [
      "[*] Using exploit/multi/handler\n[*] Listening on {lhost}:{lport}\n[+] Incoming connection from {rhost}:{rport}\n[+] Command shell session 2 opened at {now}\n[*] Handler ready",
      "[*] Handler started on {lhost}:{lport}\n[-] No connection received within timeout\n[-] Session timed out at {now}"
    ],
    "tomcat-deploy": [
      "[*] Using exploit module: exploit/multi/http/tomcat_mgr_deploy\n[*] Target: {rhost}:{rport}\n[*] Attempting deploy...\n[+] WAR deployed successfully\n[+] Reverse connection established to {lhost}:{lport} at {now}\n[*] Exploit completed",
      "[*] Deploy attempt failed: authentication required\n[-] Tomcat manager denied access\n[*] Completed at {now}"
    ],
    "smb-ms08-067": [
      "[*] Using exploit/windows/smb/ms08_067_netapi\n[*] RHOST => {rhost}\n[+] Shell opened on {rhost}:{rport}\n[+] Exploit successful, running whoami\nroot\n[*] Completed at {now}",
      "[*] Exploit attempt sent\n[-] Target did not respond to crafted packet\n[-] Exploit failed at {now}"
    ],
    "php-cgi-arg-injection": [
      "[*] Target: {rhost}:{rport}\n[*] Injecting argument payload\n[+] Command output: uid=33(www-data) gid=33(www-data)\n[+] Reverse shell attempted to {lhost}:{lport}\n[*] Completed at {now}",
      "[*] Argument injection attempt\n[-] Target sanitized input; payload rejected\n[*] Finished at {now}"
    ],
    "jenkins-script-console": [
      "[*] Connecting to Jenkins script console at {rhost}:{rport}\n[*] Executing Groovy snippet\n[+] Output: 'Hello from Jenkins'\n[*] Completed at {now}",
      "[*] Authentication required for script console\n[-] Access denied\n[*] Completed at {now}"
    ],
    "http-put-deploy": [
      "[*] Trying HTTP PUT on {rhost}:{rport}\n[+] File uploaded via PUT\n[+] Payload executed, connection to {lhost}:{lport} established\n[*] Done at {now}",
      "[*] PUT upload blocked by server configuration\n[-] Deploy failed at {now}"
    ],
    "simple-ping": [
      "PING {rhost} ({rhost}) 56(84) bytes of data.\n64 bytes from {rhost}: icmp_seq=1 ttl=64 time=0.{n} ms\n--- {rhost} ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time {n}ms",
      "PING {rhost} ({rhost}): Destination Host Unreachable\n--- {rhost} ping statistics ---\n1 packets transmitted, 0 received, 100% packet loss"
    ],
    "default": [
      "[*] Using exploit module: {exploit}\n[*] Target {rhost}:{rport}\n[*] Attempting to run payload {payload}\n[+] Action completed at {now}",
      "[*] Running module {exploit}\n[-] Target did not respond as expected\n[*] Finished at {now}"
    ]
  };

  function fillTemplate(tpl, ctx) {
    return tpl.replace(/\{(\w+)\}/g, (_, k) => {
      if (k === 'n') return String(rnd(5,400));
      if (k === 'now') return ctx.now || nowTs();
      return (ctx[k] !== undefined && ctx[k] !== null) ? ctx[k] : '';
    });
  }

  function simulateExploitFromTemplates(exploitId, ctx) {
    const arr = SIM_TEMPLATES[exploitId] || SIM_TEMPLATES['default'];
    const chosen = pick(arr);
    return fillTemplate(chosen, ctx);
  }

  // ---------- ATTACK PAGE ----------
  (function wireAttackPage() {
    const exploitSelect = document.getElementById('exploit-select');
    if (!exploitSelect) return;

    const exploitInput = document.getElementById('exploit');
    const payloadSelect = document.getElementById('payload-select');
    const rhost = document.getElementById('rhost');
    const rport = document.getElementById('rport');
    const lhost = document.getElementById('lhost');
    const lport = document.getElementById('lport');
    const mode = document.getElementById('mode');
    const outputEl = document.getElementById('output');
    const infoDesc = document.getElementById('info-desc');
    const infoTags = document.getElementById('info-tags');
    const infoNotes = document.getElementById('info-notes');
    const clearBtn = document.getElementById('clear-btn');
    const downloadLink = document.getElementById('download-link');

    // populate selector
    exploitSelect.innerHTML = '<option value="">-- choose --</option>';
    EXPLOITS.forEach(it => {
      const opt = document.createElement('option'); opt.value = it.id; opt.textContent = it.title;
      exploitSelect.appendChild(opt);
    });

    function clearPayloads() { payloadSelect.innerHTML = '<option value="">— choose payload —</option>'; }
    function setInfo(it) {
      infoDesc.textContent = it.description || '';
      infoTags.innerHTML = '';
      (it.required_fields || []).forEach(f => {
        const el = document.createElement('span'); el.className = 'tag'; el.textContent = f; infoTags.appendChild(el);
      });
      infoNotes.textContent = it.notes || '';
    }

    function setFieldVisibility(required) {
      const fields = { rhost, rport, lhost, lport, payload: payloadSelect };
      Object.entries(fields).forEach(([k, el]) => {
        if (!el) return;
        if (required.includes(k)) {
          el.closest('label')?.style?.setProperty('opacity', '1');
          el.disabled = false; el.required = true;
        } else {
          el.closest('label')?.style?.setProperty('opacity', '0.55');
          el.disabled = true; el.required = false;
          if (el.tagName === 'SELECT') el.value = '';
          else el.value = '';
        }
      });
    }

    exploitSelect.addEventListener('change', () => {
      const id = exploitSelect.value;
      if (!id) {
        exploitInput.value = ''; clearPayloads(); setInfo({ description: 'Choose an exploit to see details.' }); setFieldVisibility([]); return;
      }
      const it = EXPLOITS.find(x => x.id === id);
      if (!it) return;
      exploitInput.value = it.exploit || '';
      clearPayloads();
      (it.payloads || []).forEach(p => {
        const o = document.createElement('option'); o.value = p; o.textContent = p; payloadSelect.appendChild(o);
      });
      setFieldVisibility(it.required_fields || []);
      setInfo(it);
      if (mode) mode.value = localStorage.getItem(STORAGE_KEY) || 'simulate';
    });

    // Clear button
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        const form = document.getElementById('exploit-form');
        if (form) form.reset();
        if (outputEl) outputEl.textContent = '';
        if (downloadLink) downloadLink.style.display = 'none';
        setFieldVisibility([]);
        exploitSelect.value = '';
        exploitInput.value = '';
        clearPayloads();
        setInfo({ description: 'Choose an exploit to see details.' });
        if (mode) mode.value = localStorage.getItem(STORAGE_KEY) || 'simulate';
      });
    }

    // Fill example
    const fillBtn = document.getElementById('fill-example');
    if (fillBtn) {
      fillBtn.addEventListener('click', () => {
        const id = exploitSelect.value || (EXPLOITS[0] && EXPLOITS[0].id);
        if (!id) return alert('Choose an exploit first');
        const it = EXPLOITS.find(x => x.id === id);
        if (!it) return;
        if (it.required_fields.includes('rhost')) rhost.value = '192.168.56.101';
        if (it.required_fields.includes('rport')) rport.value = '80';
        if (it.required_fields.includes('lhost')) lhost.value = '10.0.0.5';
        if (it.required_fields.includes('lport')) lport.value = '4444';
        if (it.payloads && it.payloads.length) payloadSelect.value = it.payloads[0];
      });
    }

    // Copy button
    const copyBtn = document.getElementById('copy-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        const t = outputEl.textContent || ''; if (!t) return alert('No output'); navigator.clipboard.writeText(t).then(() => alert('Copied'));
      });
    }

    function makeDownload(text, jid) {
      if (!downloadLink) return;
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      downloadLink.href = url; downloadLink.download = (jid ? 'job-' + jid + '.txt' : 'output.txt');
      downloadLink.style.display = 'inline-block'; downloadLink.textContent = 'Download';
    }

    // submit handling
    const form = document.getElementById('exploit-form');
    if (!form) return;
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const payloadData = {
        exploit: (document.getElementById('exploit')?.value || '').trim(),
        rhost: (rhost?.value || '').trim(),
        rport: (rport?.value || '').trim(),
        payload: (payloadSelect?.value || '').trim(),
        lhost: (lhost?.value || '').trim(),
        lport: (lport?.value || '').trim(),
        mode: (mode?.value || 'simulate')
      };

      const chosen = EXPLOITS.find(x => x.exploit === payloadData.exploit || x.id === exploitSelect.value);
      if (!chosen) {
        if (outputEl) outputEl.textContent = 'Please choose an exploit template first.'; return;
      }
      for (const f of (chosen.required_fields || [])) {
        if (!payloadData[f] && payloadData[f] !== 0) {
          if (outputEl) outputEl.textContent = `Missing required field: ${f}`; return;
        }
      }

      if (outputEl) outputEl.textContent = 'Running...';

      try {
        const res = await fetch(apiUrl('/api/exploit/run'), {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payloadData)
        }).catch(e => null);
        let data = {};
        if (res) {
          try { data = await res.json(); } catch (e) { data = {}; }
        }

        if (payloadData.mode === 'simulate') {
          const ctx = {
            rhost: payloadData.rhost || '',
            rport: payloadData.rport || '',
            payload: payloadData.payload || '',
            lhost: payloadData.lhost || '',
            lport: payloadData.lport || '',
            exploit: chosen.exploit || chosen.id || '',
            now: nowTs()
          };
          const simText = simulateExploitFromTemplates(chosen.id, ctx);
          let display = simText;
          if (data && data.job_id) display += `\n\nJob ID: ${data.job_id}`;
          if (outputEl) outputEl.textContent = display;
          makeDownload(display, data && data.job_id ? data.job_id : '');
        } else {
          if (res && res.ok && data) {
            let text = '';
            if (data.output) text += data.output + '\n';
            if (data.job_id) text += '\nJob ID: ' + data.job_id + '\n';
            if (data.exit_code !== undefined) text += 'Exit code: ' + data.exit_code + '\n';
            if (outputEl) outputEl.textContent = text;
            makeDownload(text, data.job_id || '');
          } else {
            if (outputEl) outputEl.textContent = 'Error: ' + (data.error || (res ? res.status : 'network'));
          }
        }
      } catch (e) {
        if (outputEl) outputEl.textContent = 'Request failed: ' + (e.message || e);
      }
    });

    // initialize attack page state
    setFieldVisibility([]);
    setInfo({ description: 'Choose an exploit to see details.' });
    if (mode) mode.value = localStorage.getItem(STORAGE_KEY) || 'simulate';
  })();

  // ---------- AUXILIARY PAGE ----------
  (function wireAuxiliaryPage() {
    const scanTypeSelect = document.getElementById('scan-type');
    const psForm = document.getElementById('portscan-form');
    const httpForm = document.getElementById('http-form');
    const pingForm = document.getElementById('ping-form');

    if (scanTypeSelect) {
      const psCard = document.getElementById('ps-card');
      const httpCard = document.getElementById('http-card');
      const pingCard = document.getElementById('ping-card');

      function showScanCard(type) {
        if (psCard) psCard.style.display = (type === 'tcp') ? 'block' : 'none';
        if (httpCard) httpCard.style.display = (type === 'http') ? 'block' : 'none';
        if (pingCard) pingCard.style.display = (type === 'ping') ? 'block' : 'none';
        const cur = localStorage.getItem(STORAGE_KEY) || 'simulate';
        const psSim = document.getElementById('ps-simulate');
        const httpSim = document.getElementById('http-simulate');
        const pingSim = document.getElementById('ping-simulate');
        if (psSim) psSim.checked = (cur === 'simulate');
        if (httpSim) httpSim.checked = (cur === 'simulate');
        if (pingSim) pingSim.checked = (cur === 'simulate');
      }

      scanTypeSelect.addEventListener('change', () => showScanCard(scanTypeSelect.value));
      showScanCard(scanTypeSelect.value || 'tcp');
    }

    // portscan handler
    if (psForm) {
      const psOutput = document.getElementById('ps-output');
      psForm.addEventListener('submit', async (ev) => {
        ev.preventDefault();
        if (psOutput) psOutput.textContent = '';
        const rhost = (document.getElementById('ps-rhost')?.value || '').trim();
        const start_port = parseInt(document.getElementById('ps-start')?.value || '1', 10);
        const end_port = parseInt(document.getElementById('ps-end')?.value || '1024', 10);
        const simulateChecked = document.getElementById('ps-simulate')?.checked ?? true;
        if (!rhost) return alert('RHOST required');
        if (simulateChecked || (localStorage.getItem(STORAGE_KEY) || 'simulate') === 'simulate') {
          if (psOutput) psOutput.textContent = simulatePortScan(rhost, start_port, end_port);
          return;
        }
        try {
          const resp = await fetch(apiUrl('/api/aux/portscan_tcp'), {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rhost, start_port, end_port })
          });
          const data = await resp.json();
          if (resp.ok) psOutput.textContent = JSON.stringify(data, null, 2);
          else psOutput.textContent = 'Error: ' + (data.error || resp.status);
        } catch (e) {
          psOutput.textContent = 'Request failed: ' + (e.message || e);
        }
      });
      const psClear = document.getElementById('ps-clear');
      if (psClear) psClear.addEventListener('click', () => { psForm.reset(); const out = document.getElementById('ps-output'); if (out) out.textContent = ''; });
    }

    // http handler
    if (httpForm) {
      const httpOutput = document.getElementById('http-output');
      httpForm.addEventListener('submit', async (ev) => {
        ev.preventDefault();
        if (httpOutput) httpOutput.textContent = '';
        const urlVal = (document.getElementById('http-url')?.value || '').trim();
        const simulateChecked = document.getElementById('http-simulate')?.checked ?? true;
        if (!urlVal) return alert('URL required');
        if (simulateChecked || (localStorage.getItem(STORAGE_KEY) || 'simulate') === 'simulate') {
          if (httpOutput) httpOutput.textContent = simulateHttpCheck(urlVal);
          return;
        }
        try {
          const resp = await fetch(apiUrl('/api/aux/http_version'), {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: urlVal })
          });
          const data = await resp.json();
          if (resp.ok) httpOutput.textContent = JSON.stringify(data, null, 2);
          else httpOutput.textContent = 'Error: ' + (data.error || resp.status);
        } catch (e) { httpOutput.textContent = 'Request failed: ' + (e.message || e); }
      });
      const httpClear = document.getElementById('http-clear');
      if (httpClear) httpClear.addEventListener('click', () => { httpForm.reset(); const out = document.getElementById('http-output'); if (out) out.textContent = ''; });
    }

    // ping handler
    if (pingForm) {
      const pingOutput = document.getElementById('ping-output');
      pingForm.addEventListener('submit', async (ev) => {
        ev.preventDefault();
        if (pingOutput) pingOutput.textContent = '';
        const rhost = (document.getElementById('ping-rhost')?.value || '').trim();
        const simulateChecked = document.getElementById('ping-simulate')?.checked ?? true;
        if (!rhost) return alert('RHOST required');
        if (simulateChecked || (localStorage.getItem(STORAGE_KEY) || 'simulate') === 'simulate') {
          if (pingOutput) pingOutput.textContent = simulatePing(rhost);
          return;
        }
        try {
          const resp = await fetch(apiUrl('/api/aux/ping'), {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ rhost })
          });
          const data = await resp.json();
          if (resp.ok) pingOutput.textContent = JSON.stringify(data, null, 2);
          else pingOutput.textContent = 'Error: ' + (data.error || resp.status);
        } catch (e) { pingOutput.textContent = 'Request failed: ' + (e.message || e); }
      });
      const pingClear = document.getElementById('ping-clear');
      if (pingClear) pingClear.addEventListener('click', () => { pingForm.reset(); const out = document.getElementById('ping-output'); if (out) out.textContent = ''; });
    }
  })();

  // Make sure header toggle exists if DOM changed later
  ensureHeaderToggle();

})(); 
