# Readability-first source extraction

Direct Source Requests will first extract article content with a simple fetch and readability parser, then fall back to Playwright for sources that require browser rendering. This keeps the local MVP lightweight for normal news pages while preserving a path for JavaScript-heavy sources without using an external extraction API.
