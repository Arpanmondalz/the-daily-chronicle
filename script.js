document.addEventListener('DOMContentLoaded', fetchNews);

async function fetchNews() {
    const container = document.getElementById('news-container');
    const timestampEl = document.getElementById('last-updated');

    try {
        const response = await fetch('news.json');
        if (!response.ok) throw new Error("Could not find news.json");
        
        const data = await response.json();
        
        timestampEl.textContent = `Last Inscribed: ${data.last_updated}`;
        container.innerHTML = '';

        data.stories.forEach(story => {
            const card = document.createElement('article');
            card.className = 'story-card';

            let summary = story.original_summary || "";
            if (summary && !summary.endsWith('.')) {
                summary += '...';
            }

            card.innerHTML = `
                <div class="fantasy-content">
                    <h2 class="fantasy-title">${story.fantasy_headline}</h2>
                    <p class="fantasy-body">${story.fantasy_story}</p>
                </div>

                <button class="reveal-btn" onclick="toggleRealNews(this)">
                    👁 Reveal Reality
                </button>

                <div class="real-content">
                    <div class="real-headline">${story.original_headline}</div>
                    <p class="real-summary">${summary}</p>
                    <a href="${story.id}" target="_blank" class="source-link">Read Original Source &rarr;</a>
                </div>
            `;
            container.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        container.innerHTML = `<div style="text-align:center; color:#888;">Alas! The scrolls could not be summoned.<br><small>${error.message}</small></div>`;
    }
}

window.toggleRealNews = function(btn) {
    const card = btn.parentElement;
    const realContent = card.querySelector('.real-content');
    const isHidden = realContent.style.display === 'none' || realContent.style.display === '';
    
    if (isHidden) {
        realContent.style.display = 'block';
        btn.innerHTML = '⋆˙⟡ Return to Fantasy';
        btn.style.borderColor = '#6495ed';
        btn.style.color = '#6495ed';
    } else {
        realContent.style.display = 'none';
        btn.innerHTML = '👁 Reveal Reality';
        btn.style.borderColor = '#555';
        btn.style.color = '#888';
    }
};
