---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, language, sort_by, limit]
outputs: [items, total_count]
side_effect: false
---
# github_search

Searches public GitHub repositories by keyword, programming language, and sort order.
Useful for finding open-source code implementations of AI research papers, libraries, and tools.

