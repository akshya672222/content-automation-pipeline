# content-automation-pipeline

> Production-ready AI content automation pipeline using Claude API — multi-platform publishing for LinkedIn, Medium, and X with fabrication prevention and validation layers.
>
> 📖 **Read the full article on Medium**: [Why Your AI Content Automation Sounds Fake — And How I Fixed It](https://medium.com/@akshya672222)
>
> ---
>
> ## Overview
>
> This repo contains the implementation behind my personal content automation system. It generates platform-optimized technical content using Claude API while maintaining voice authenticity through strict fabrication prevention rules.
>
> Built and maintained by a senior iOS engineer at Microsoft Teams. Battle-tested in production for 6+ months.
>
> ---
>
> ## Architecture
>
> ```
> content-automation-pipeline/
> ├── pipeline/
> │   ├── content_pipeline.py       # Core orchestration
> │   ├── claude_client.py          # Claude API wrapper with retry + caching
> │   └── validator.py              # Multi-layer content validation
> ├── publishers/
> │   ├── linkedin_publisher.py     # Playwright-based browser automation
> │   ├── medium_publisher.py       # Medium REST API publisher
> │   └── twitter_publisher.py      # X v2 API publisher
> ├── swift/
> │   └── StoryValidationPipeline.swift  # iOS validation (ParentPal pattern)
> ├── .env.example                  # API key template
> └── README.md
> ```
>
> ---
>
> ## Key Features
>
> - **Fabrication Prevention** — System prompt rules that prevent AI hallucination of career events, metrics, and anecdotes
> - - **Multi-Platform Publishing** — LinkedIn (Playwright), Medium (REST API), X (v2 API)
>   - - **Retry Logic** — Exponential backoff with jitter for rate limit handling
>     - - **Prompt Caching** — Anthropic cache_control for ~50% cost reduction
>       - - **Concurrent Generation** — asyncio.gather for parallel platform content
>         - - **Bounded Repair Cycles** — Swift validation with depth guard (no infinite recursion)
>          
>           - ---
>
> ## Setup
>
> ```bash
> git clone https://github.com/akshya672222/content-automation-pipeline
> cd content-automation-pipeline
> pip install -r requirements.txt
> cp .env.example .env
> # Add your ANTHROPIC_API_KEY to .env
> ```
>
> ---
>
> ## LinkedIn Publisher Note
>
> The LinkedIn publisher uses Playwright browser automation since LinkedIn has no public posting API for personal profiles. CSS selectors are abstracted into named helper methods and kept up to date in this repo as LinkedIn ships UI changes.
>
> > ⚠️ LinkedIn UI changes frequently. If selectors break, check the [Issues](https://github.com/akshya672222/content-automation-pipeline/issues) tab or open a PR with updated selectors.
> >
> > ---
> >
> > ## Requirements
> >
> > - Python 3.11+
> > - - Anthropic API key
> >   - - Playwright (`playwright install chromium`)
> >     - - X Developer API v2 credentials (for Twitter publishing)
> >       - - Medium Integration Token (for Medium publishing)
> >        
> >         - ---
> >
> > ## License
> >
> > MIT — see [LICENSE](./LICENSE)
