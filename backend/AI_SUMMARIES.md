# Local AI summary setup

Source retrieval and the in-app reader still work without AI configuration.
The backend sends the retrieved public page text to the Groq Chat Completions API to
produce a short plain-English summary. No API key belongs in React or GitHub.

Add this to your existing private `backend/.env` file (do not replace other settings):

```dotenv
GROQ_API_KEY=your_private_api_key
```

Restart Flask after saving. Load a supported source in Resources; its summary
appears above the existing reader button. Use a GroqCloud account on the Free Plan. Free-tier request and token limits apply;
requests that exceed them fail rather than producing a summary. No OpenAI key is used.

The default model is `openai/gpt-oss-20b`. Optionally set `GROQ_SUMMARY_MODEL` in the
backend environment to another Groq Chat Completions model supporting the configured reasoning parameters. Never prefix the key
with `VITE_` or place it in frontend files. Do not commit your `.env`.

## Behavior and limits

- Prompts ask for 100–180 words using only the extracted source, preserving
  important conditions and exceptions. AI output is not guaranteed accurate.
- Documents over 16,000 characters are not summarized; text is never silently
  truncated. The original reader remains available.
- Responses must be complete and contain text before they are shown.
- Up to 100 summaries are cached in memory for one hour by source text and model.
- At most 10 new AI requests per minute per server process; this is a development
  safeguard, not a shared production usage quota. A production release needs
  account-level limits and shared caching before public usage.
- Failures return a summary status alongside the original source, not a fake summary.
- The API request uses a 35-second timeout, a 2,048-token completion budget,
  low reasoning effort, and excludes reasoning from the displayed content.
- The 16,000-character source limit leaves room for instructions and output under
  typical free-tier limits. Token counts vary; Groq can still return a rate-limit
  error. Text is never silently truncated.
- The model name starts with `openai/` because OpenAI created its open-weight
  model; Groq hosts it and receives this request. It does not call the OpenAI API.

Run isolated resource tests without a database:

```bash
python -m unittest discover -s backend/resource_tests -v
```

Reference: https://console.groq.com/docs/text-chat
https://console.groq.com/docs/rate-limits
