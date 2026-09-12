document.addEventListener('DOMContentLoaded', async () => {
  const searchInput = document.getElementById('searchInput');
  const searchBtn = document.getElementById('searchBtn');
  const resultsContainer = document.getElementById('resultsContainer');
  const loadingIndicator = document.getElementById('loadingIndicator');
  const examplesContainer = document.getElementById('examplesContainer');

  // Load Meta & Examples
  try {
    const metaRes = await fetch('/api/meta');
    const metaData = await metaRes.json();
    if (metaData.examples) {
      metaData.examples.forEach(ex => {
        const tag = document.createElement('div');
        tag.className = 'example-tag';
        tag.textContent = ex.query;
        tag.onclick = () => {
          searchInput.value = ex.query;
          performSearch(ex.query);
        };
        examplesContainer.appendChild(tag);
      });
    }
  } catch (e) {
    console.error('Failed to load metadata', e);
  }

  searchBtn.addEventListener('click', () => {
    const q = searchInput.value.trim();
    if (q.length > 1) performSearch(q);
  });

  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const q = searchInput.value.trim();
      if (q.length > 1) performSearch(q);
    }
  });

  async function performSearch(query) {
    resultsContainer.innerHTML = '';
    loadingIndicator.style.display = 'flex';
    
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      
      loadingIndicator.style.display = 'none';
      renderResults(data);
    } catch (e) {
      loadingIndicator.style.display = 'none';
      resultsContainer.innerHTML = `<div style="color: #ef4444; text-align: center;">Error performing search. Is the server running?</div>`;
    }
  }

  function renderResults(data) {
    if (!data.hits || data.hits.length === 0) {
      resultsContainer.innerHTML = `<div style="text-align: center; color: var(--text-muted);">No results found.</div>`;
      return;
    }

    data.hits.forEach(hit => {
      const card = document.createElement('div');
      card.className = 'hit-card';

      // Meta Header
      const meta = document.createElement('div');
      meta.className = 'hit-meta';
      
      const score = document.createElement('div');
      score.className = 'hit-score';
      score.textContent = `Score: ${hit.score}`;

      const tags = document.createElement('div');
      tags.className = 'hit-tags';
      hit.why.forEach(w => {
        const span = document.createElement('span');
        span.className = 'why-tag';
        if (w.startsWith('time:')) span.classList.add('time');
        if (w.startsWith('person:')) span.classList.add('person');
        if (w.startsWith('meaning:')) span.classList.add('meaning');
        span.textContent = w;
        tags.appendChild(span);
      });

      meta.appendChild(score);
      meta.appendChild(tags);
      card.appendChild(meta);

      // Chat Window
      const chatWindow = document.createElement('div');
      chatWindow.className = 'chat-window';
      
      hit.context.forEach(msg => {
        const bubble = document.createElement('div');
        // Simple heuristic: alternate sides, or specific users on right
        const isRight = ['Rohit', 'Devansh', 'Aman'].includes(msg.sender);
        bubble.className = `chat-bubble ${isRight ? 'right' : 'left'}`;
        if (msg.is_hit) bubble.classList.add('is-hit');

        const sender = document.createElement('div');
        sender.className = 'bubble-sender';
        sender.textContent = msg.sender;

        const content = document.createElement('div');
        content.className = 'bubble-content';
        
        let text = msg.text;
        if (msg.kind === 'media_omitted') {
          text = '📷 <Media omitted>';
        } else if (msg.kind === 'forwarded') {
          text = `⏩ Forwarded:\n${text}`;
        }
        content.textContent = text;

        const time = document.createElement('div');
        time.className = 'bubble-meta';
        const date = new Date(msg.ts);
        time.textContent = `${date.getDate()} ${date.toLocaleString('default', { month: 'short' })} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;

        content.appendChild(time);
        bubble.appendChild(sender);
        bubble.appendChild(content);
        chatWindow.appendChild(bubble);
      });

      card.appendChild(chatWindow);
      resultsContainer.appendChild(card);
    });
  }
});
