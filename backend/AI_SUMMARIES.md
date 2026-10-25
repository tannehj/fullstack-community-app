# Local AI summary setup

Source retrieval and the in-app reader still work without AI configuration.
The backend sends the retrieved public page text to the OpenAI Responses API to
produce a short plain-English summary. No API key belongs in React or GitHub.

Add this to your existing private `backend/.env` file (do not replace other settings):

```dotenv
OPENAI_API_KEY=your_private_api_key
```

Restart Flask after saving. Load a supported source in Resources; its summary
appears above the existing reader button. API usage requires an OpenAI API
account with billing/credits and model access; a ChatGPT subscription is separate.

The default model is `gpt-4.1-mini`. Optionally set `OPENAI_SUMMARY_MODEL` in the
backend environment to another Responses-compatible model. Never prefix the key
with `VITE_` or place it in frontend files. Do not commit your `.env`.

## Behavior and limits

- Prompts ask for 100–180 words using only the extracted source, preserving
  important conditions and exceptions. AI output is not guaranteed accurate.
- Documents over 60,000 characters are not summarized; text is never silently
  truncated. The original reader remains available.
- Responses must be complete and contain text before they are shown.
- Up to 100 summaries are cached in memory for one hour by source text and model.
- At most 10 new AI requests per minute per server process; this is a development
  safeguard, not a shared production usage quota. A production release needs
  account-level limits and shared caching before public usage.
- Failures return a summary status alongside the original source, not a fake summary.
- The API request uses `store: false` and a 35-second timeout.

Run isolated resource tests without a database:

```bash
python -m unittest discover -s backend/resource_tests -v
```

Reference: https://developers.openai.com/api/docs/guides/text
