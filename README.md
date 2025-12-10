# The Daily Chronicle

**The Daily Chronicle** is a playful news portal that turns real headlines into short medieval-fantasy stories.  
Every 4 hours, a script fetches fresh news, runs it through an AI (gemini 2.5 flash), and publishes the transformed tales as a minimalist web experience.

Live site: **https://arpanmondalz.github.io/the-daily-chronicle**

---

## How it works

### 1. Data collection

A Python script (run via GitHub Actions on a schedule) does the following:

- Fetches headlines and summaries from a curated set of RSS feeds (science, tech, world, business).
- Cleans and deduplicates the items.
- Sends a batch of items to the Gemini API with a strict prompt:
  - Check if each story is safe (no mass violence, hate, etc.).
  - If safe, rewrite it as a short, accessible medieval-fantasy story.
  - If not, mark it as skipped.
- Saves the result to a simple JSON file:

```
{
  "last_updated": "2025-12-05 20:46:09",
  "stories": [
    {
      "id": "https://example.com/news-article",
      "status": "published",
      "reason": null,
      "original_headline": "Real world headline",
      "original_summary": "Short real summary...",
      "fantasy_headline": "Fantasy styled headline",
      "fantasy_story": "Fantasy styled short story.",
      "tag": "magic"
    }
  ]
}
```

This `news.json` file is committed back to the repo so the frontend can stay fully static.

---

### 2. Frontend

The site is intentionally simple: **pure HTML, CSS, and vanilla JavaScript**.

- Fetches `news.json` from the same repo.
- Displays each story as a “card”:
  - **Fantasy headline** in a fantasy-style font.
  - **Fantasy story** in clear, modern English with a fantasy flavour.
- Each card has a button:

  - **“Reveal Reality 👁️”** – shows:
    - The original headline.
    - The original summary (trimmed with `...` if necessary).
    - A link to the source article.

Clicking again hides the real-world info and returns to the fantasy view.

The visual design:

- Dark, book-like theme.
- Headings using **Eagle Lake**.
- Body text using **Crimson Text**.
- Focus on readability and atmosphere rather than heavy graphics.

---

## Repository structure (key files)

- `index.html` – Main page layout.
- `style.css` – Typography and theming.
- `script.js` – Fetches `news.json` and handles “Reveal Reality” toggling.
- `news.json` – Latest generated stories (updated by the workflow).
- `update_news.py`– Python script that fetches RSS feeds and calls Gemini.
- `.github/workflows/update_news.yml` – GitHub Actions workflow that:
  - Installs dependencies.
  - Runs the Python script every few hours.
  - Commits updated `news.json` back to `main`.

---

## Running locally

You can view the site locally without touching the automation:

1. Clone the repo:

   ```
   git clone https://github.com/Arpanmondalz/the-daily-chronicle.git
   cd the-daily-chronicle
   ```

2. Start a simple HTTP server (so `fetch('news.json')` works):

   ```
   # Python 3
   python -m http.server 8000
   ```

3. Open your browser at:  
   `http://localhost:8000`

You should see the latest fantasy news exactly as on GitHub Pages.

---

## Regenerating stories (optional)

If you want to regenerate stories yourself (outside of GitHub Actions):

1. Install Python dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set your Gemini API key as an environment variable:

   ```
   export API_KEY="YOUR_GEMINI_API_KEY"
   ```

3. Run the update script:

   ```
   python update_news.py
   ```

4. Commit and push the new `news.json` if you want it live.

> Note: The public workflow in this repo is configured to use a GitHub Actions secret for the API key.  
> The key must never be committed to the repo.

---

## Tech stack

- **Backend automation**
  - Python
  - RSS (feedparser, BeautifulSoup)
  - Gemini API (HTTP via `requests`)
  - GitHub Actions (scheduled workflow)

- **Frontend**
  - Static HTML / CSS
  - Vanilla JavaScript (`fetch`, DOM updates)
  - Hosted on **GitHub Pages**

---

## About

Built by **Arpan Mondal** as a small art-engineering experiment:  
