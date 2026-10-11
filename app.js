const UI_STRINGS = {
  en: {
    loading: "Synthesizing latest briefings...",
    editionPrefix: "EDITION",
    all: "ALL (45)",
    breaking: "🔴 BREAKING (10)",
    india: "🇮🇳 INDIA (5)",
    finance: "📊 FINANCE (10)",
    crypto: "🪙 CRYPTO (10)",
    viral: "🔥 VIRAL (10)",
    secTitles: {
      breaking: "Global Breaking News",
      india: "What's New in India",
      finance: "Global Financial Markets",
      crypto: "Crypto & Blockchain News",
      viral: "Social Trends & Viral Pulse"
    }
  },
  hi: {
    loading: "नवीनतम समाचार बुलेटिन संकलित हो रहा है...",
    editionPrefix: "संस्करण",
    all: "सभी (45)",
    breaking: "🔴 ब्रेकिंग (10)",
    india: "🇮🇳 भारत (5)",
    finance: "📊 वित्त (10)",
    crypto: "🪙 क्रिप्टो (10)",
    viral: "🔥 ट्रेंडिंग (10)",
    secTitles: {
      breaking: "वैश्विक ब्रेकिंग न्यूज़",
      india: "भारत में नया क्या है",
      finance: "वैश्विक वित्तीय बाज़ार",
      crypto: "क्रिप्टो और ब्लॉकचेन समाचार",
      viral: "सोशल मीडिया और वायरल ट्रेंड्स"
    }
  }
};

let currentLang = 'en';
let currentFilter = 'all';
let newsData = null;

const langSwitch = document.getElementById('langSwitch');
const switchPill = langSwitch.querySelector('.switch-pill');
const optEN = document.getElementById('optEN');
const optHI = document.getElementById('optHI');
const feedContainer = document.getElementById('feedContainer');
const editionLabel = document.getElementById('editionLabel');

langSwitch.addEventListener('click', () => {
  currentLang = currentLang === 'en' ? 'hi' : 'en';
  if (currentLang === 'hi') {
    switchPill.classList.add('hindi');
    optHI.classList.add('active');
    optEN.classList.remove('active');
  } else {
    switchPill.classList.remove('hindi');
    optEN.classList.add('active');
    optHI.classList.remove('active');
  }
  updateUILabels();
  renderFeed();
});

function updateUILabels() {
  const s = UI_STRINGS[currentLang];
  document.getElementById('chipAll').textContent = s.all;
  document.getElementById('chipBreaking').textContent = s.breaking;
  document.getElementById('chipIndia').textContent = s.india;
  document.getElementById('chipFinance').textContent = s.finance;
  document.getElementById('chipCrypto').textContent = s.crypto;
  document.getElementById('chipViral').textContent = s.viral;
  if (newsData && newsData.edition) {
    editionLabel.textContent = `${newsData.edition.toUpperCase()} ${s.editionPrefix}`;
  }
}

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', (e) => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    e.currentTarget.classList.add('active');
    currentFilter = e.currentTarget.getAttribute('data-cat');
    renderFeed();
  });
});

function renderFeed() {
  if (!newsData || !newsData[currentLang]) return;
  const content = newsData[currentLang];
  const titles = UI_STRINGS[currentLang].secTitles;
  feedContainer.innerHTML = '';

  const categories = currentFilter === 'all' 
    ? ['breaking', 'india', 'finance', 'crypto', 'viral'] 
    : [currentFilter];

  categories.forEach(cat => {
    const items = content[cat] || [];
    if (!items.length) return;

    const block = document.createElement('div');
    block.className = 'category-block';

    const header = document.createElement('div');
    header.className = 'category-title';
    header.textContent = titles[cat];
    block.appendChild(header);

    items.forEach(point => {
      const card = document.createElement('div');
      card.className = 'point-card-3d';
      const match = point.match(/^(\d+\.)\s*(.*)$/);
      if (match) {
        card.innerHTML = `<span class="point-number">${match[1]}</span><span class="point-text">${match[2]}</span>`;
      } else {
        card.innerHTML = `<span class="point-text">${point}</span>`;
      }
      block.appendChild(card);
    });

    feedContainer.appendChild(block);
  });
}

async function loadBriefing() {
  try {
    const res = await fetch('data/news-crux.json?t=' + Date.now());
    newsData = await res.json();
    updateUILabels();
    renderFeed();
  } catch (err) {
    feedContainer.innerHTML = `<p style="text-align:center; color: #ef4444; margin-top: 30px;">Tap refresh to load data.</p>`;
  }
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}

loadBriefing();
