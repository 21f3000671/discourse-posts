# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web scraping and data collection system for the IIT Madras "Tools in Data Science" (TDS) course. The project scrapes educational content from the TDS website and discussion forum data from the IIT Madras Discourse platform to build a knowledge base for an LLM-based virtual teaching assistant.

## Architecture

The system follows a three-stage pipeline:

1. **Authentication**: `get_cookies.py` uses Selenium to authenticate with the Discourse platform and saves session cookies to `discourse_cookies.pkl`
2. **Web Scraping**: `scrap_topics.py` loads saved cookies and scrapes topic metadata using requests + BeautifulSoup
3. **Data Storage**: Collected data is stored in JSONL format for efficient processing

## Key Data Sources

- **CourseContentData.jsonl**: 558 records of course curriculum covering 7 modules (Development Tools, Deployment, LLMs, Data Sourcing, Data Preparation, Data Analysis, Data Visualization)
- **DicourseData.jsonl**: 3,380 discussion forum records with student questions and instructor responses
- **topics.json**: Topic metadata from the Knowledge Base category

## Development Commands

```bash
# Authentication (run first)
python get_cookies.py

# Data collection
python scrap_topics.py

# Dependencies (inferred from imports)
pip install selenium webdriver-manager requests beautifulsoup4
```

## Important Patterns

### Authentication Flow
- Uses browser automation (Selenium + Chrome WebDriver) for initial login
- Persists cookies via pickle for subsequent API calls
- Requires manual credential update in code

### Data Structure
- JSONL format for streaming processing
- Consistent field naming: `id`, `title`, `url`, `content`, `username`, `created_at`
- Preserves source URLs for data provenance

### Error Handling
- Scripts continue processing if individual items fail
- HTTP status code validation before parsing
- Try-catch blocks around critical operations

## Security Notes

- Credentials are hardcoded in authentication scripts (security risk)
- No rate limiting implemented
- Uses realistic User-Agent headers to avoid detection