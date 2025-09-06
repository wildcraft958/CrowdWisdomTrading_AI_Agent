# Environment Configuration

## Setup Instructions

1. **Copy the template file:**
   ```bash
   cp configs/.env.template configs/.env
   ```

2. **Fill in your API keys in `configs/.env`:**
   - `OPENROUTER_API_KEY`: Get from https://openrouter.ai/
   - `SEC_IDENTITY`: Your email address for SEC EDGAR API compliance
   - `TWINWORD_API_KEY`: Get from https://www.twinword.com/api/
   - `SCRAPINGDOG_API_KEY`: Get from https://scrapingdog.com/
   - `TWITTER_BEARER_TOKEN`: Optional, get from Twitter Developer Portal

3. **Security Note:**
   - The `.env` file is automatically ignored by git
   - Never commit real API keys to the repository
   - Use the `.env.template` file as a reference

## Environment Variables

### Required
- `OPENROUTER_API_KEY`: For LLM-powered analysis and reporting
- `SEC_IDENTITY`: Email address for SEC EDGAR API access

### Optional
- `TWINWORD_API_KEY`: For enhanced sentiment analysis
- `SCRAPINGDOG_API_KEY`: For web scraping sentiment data
- `TWITTER_BEARER_TOKEN`: For premium Twitter sentiment analysis

### Configuration
- `DEFAULT_LLM_MODEL`: Default model for OpenRouter (free tier available)
- `MAX_RETRIES`: Number of retry attempts for API calls
- `RETRY_DELAY`: Delay between retry attempts in seconds
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
