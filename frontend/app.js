// app.js – Utilities, config loader, network helper, prefs, simple validation

const UI = {
  qs: (s, el=document) => el.querySelector(s),
  qsa: (s, el=document) => [...el.querySelectorAll(s)],
  toast(msg, type='info') {
    let t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(()=> t.classList.add('show'), 10);
    setTimeout(()=> { t.classList.remove('show'); setTimeout(()=>t.remove(), 300); }, 2500);
  },
  setLoading(el, on=true, text='מריץ...') {
    if (!el) return;
    if (on) {
      el.dataset.prev = el.textContent;
      el.disabled = true;
      el.textContent = text;
    } else {
      el.disabled = false;
      el.textContent = el.dataset.prev || 'הרץ';
    }
  },
  copy(text) {
    navigator.clipboard.writeText(text).then(()=> UI.toast('הועתק!', 'success'));
  }
};

const AppConfig = {
  value: { apiBase:'', defaultMode:'simulate' },
  async load() {
    const res = await fetch('config.json', { cache: 'no-store' });
    AppConfig.value = await res.json();
    return AppConfig.value;
  }
};

const Net = {
  async post(path, body) {
    const url = `${AppConfig.value.apiBase}${path}`;
    const resp = await fetch(url, {
      method:'POST',
      headers:{ 'Content-Type':'application/json' },
      body: JSON.stringify(body)
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }
};

function isIpLike(s) {
  if (!s) return false;
  const ip = /^(\d{1,3}\.){3}\d{1,3}$/;
  const host = /^[A-Za-z0-9.-]+$/;
  return ip.test(s) || host.test(s);
}

const Prefs = {
  save(key, val) { localStorage.setItem(key, JSON.stringify(val)); },
  load(key, def=null) { try { return JSON.parse(localStorage.getItem(key)) ?? def } catch { return def; } }
};

window.App = { UI, AppConfig, Net, isIpLike, Prefs };
