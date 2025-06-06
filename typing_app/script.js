const sentences = [
  { jp: '今日は良い天気です。', romaji: 'kyou wa ii tenki desu.' },
  { jp: '明日は学校に行きます。', romaji: 'ashita wa gakkou ni ikimasu.' },
  { jp: '寿司が好きですか？', romaji: 'sushi ga suki desu ka?' },
  { jp: '週末は友達と映画を見ました。', romaji: 'shuumatsu wa tomodachi to eiga o mimashita.' },
  { jp: 'プログラミングは楽しい。', romaji: 'puroguramingu wa tanoshii.' }
];

let target = '';
let current = 0;
let correct = 0;
let startTime = null;
let timerInterval = null;

const sentenceEl = document.getElementById('sentence');
const romajiEl = document.getElementById('romaji');
const inputEl = document.getElementById('input');
const timerEl = document.getElementById('timer');
const typedCountEl = document.getElementById('typed-count');
const totalCountEl = document.getElementById('total-count');
const resultEl = document.getElementById('result');
const resultTimeEl = document.getElementById('result-time');
const resultAccuracyEl = document.getElementById('result-accuracy');
const resultWpmEl = document.getElementById('result-wpm');
const highScoreEl = document.getElementById('high-score');
const restartBtn = document.getElementById('restart');

function pickSentence() {
  const s = sentences[Math.floor(Math.random() * sentences.length)];
  target = s.romaji;
  sentenceEl.textContent = s.jp;
  totalCountEl.textContent = target.length;
  renderHighlight('');
}

function updateTimer() {
  const diff = Date.now() - startTime;
  const sec = Math.floor(diff / 1000);
  const min = String(Math.floor(sec / 60)).padStart(2, '0');
  const secStr = String(sec % 60).padStart(2, '0');
  timerEl.textContent = `${min}:${secStr}`;
}

function renderHighlight(input) {
  let html = '';
  for (let i = 0; i < target.length; i++) {
    const ch = target[i];
    if (i < input.length) {
      if (input[i] === ch) {
        html += `<span class="correct">${ch}</span>`;
      } else {
        html += `<span class="incorrect">${ch}</span>`;
      }
    } else {
      html += `<span>${ch}</span>`;
    }
  }
  romajiEl.innerHTML = html;
}

function playBeep() {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = ctx.createOscillator();
  osc.frequency.value = 440;
  osc.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + 0.1);
}

function finish() {
  clearInterval(timerInterval);
  inputEl.disabled = true;
  const elapsed = (Date.now() - startTime) / 1000;
  const accuracy = correct / target.length * 100;
  const wpm = (correct / 5) / (elapsed / 60);
  resultTimeEl.textContent = `${elapsed.toFixed(2)}s`;
  resultAccuracyEl.textContent = accuracy.toFixed(1);
  resultWpmEl.textContent = wpm.toFixed(1);
  const best = Math.max(wpm, parseFloat(localStorage.getItem('jp_typing_highscore') || '0'));
  localStorage.setItem('jp_typing_highscore', best.toFixed(1));
  highScoreEl.textContent = best.toFixed(1);
  resultEl.classList.remove('hidden');
}

function reset() {
  current = 0;
  correct = 0;
  inputEl.value = '';
  inputEl.disabled = false;
  resultEl.classList.add('hidden');
  pickSentence();
  typedCountEl.textContent = '0';
  timerEl.textContent = '00:00';
  startTime = null;
  clearInterval(timerInterval);
  timerInterval = null;
  inputEl.focus();
}

inputEl.addEventListener('input', (e) => {
  if (startTime === null) {
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
  }
  const val = inputEl.value;
  const lastIndex = val.length - 1;
  if (e.inputType && !e.inputType.startsWith('delete')) {
    if (val[lastIndex] !== target[lastIndex]) {
      playBeep();
    }
  }
  current = val.length;
  correct = 0;
  for (let i = 0; i < current; i++) {
    if (val[i] === target[i]) correct++;
  }
  typedCountEl.textContent = current;
  renderHighlight(val);
  if (current >= target.length) {
    finish();
  }
});

restartBtn.addEventListener('click', reset);

window.addEventListener('load', () => {
  const best = localStorage.getItem('jp_typing_highscore');
  if (best) {
    highScoreEl.textContent = best;
  }
  reset();
});
