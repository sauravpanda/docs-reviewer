# Documentation Reviewer

An AI-powered agent that reviews documentation websites using the Browser Use Cloud API and provides critical feedback for improvements.

## Features

- 🤖 **AI-Powered Analysis**: Uses GPT-4o through Browser Use Cloud API for intelligent, contextual feedback  
- ☁️ **Cloud-Based Automation**: Leverages Browser Use Cloud API for reliable, scalable browser automation
- 📊 **Comprehensive Scoring**: Rates pages on content quality, structure, UX, and technical accuracy
- 📈 **Site-Wide Analytics**: Provides overall site statistics and improvement recommendations
- 📄 **Detailed Reports**: Generates JSON reports with actionable insights
- 🔍 **Multi-Page Review**: Automatically discovers and reviews all documentation pages
- 🚫 **No Local Browser Required**: Uses cloud infrastructure for browser automation
- ⚡ **Multiple Review Modes**: Choose between one-shot (fast), multi-step (detailed), or exhaustive (complete site crawling)
- 🕷️ **Web Crawling**: Exhaustive mode discovers ALL pages by recursively following links across the entire site
- 🔑 **Single API Key**: Only requires Browser Use API token - no separate OpenAI key needed
- 👀 **Live Automation Viewing**: Watch browser automation live via public share URLs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Copy the configuration template:
```bash
cp config.template.env .env
```

Edit `.env` and add your API token:
```
BROWSER_USE_API_TOKEN=your_browser_use_api_token_here
```

**Getting Your API Token:**
- **Browser Use API Token**: Sign up at [browser-use.com](https://browser-use.com) to get your API token

### 3. Run the Reviewer

```bash
# Default: Multi-step approach 
python docs_reviewer.py

# Or use the command-line interface
python run_review.py

# Try the one-shot approach (faster, but less detailed)
python run_review.py --approach one-shot

# EXHAUSTIVE MODE: Discover and review ALL pages on the site
python run_review.py --exhaustive

# Exhaustive with one-shot approach (review all pages in one task)
python run_review.py --exhaustive --approach one-shot

# Review a custom site with specific settings
python run_review.py https://docs.example.com --max-pages 15 --approach multi-step
```

The tool will automatically review the Browser Use documentation at `https://docs.browser-use.com/introduction` and generate a comprehensive report.

## Why Browser Use Cloud API?

Using the Browser Use Cloud API instead of the local library provides several advantages:

- **🚀 No Setup Required**: No need to install or manage local browsers
- **☁️ Scalable Infrastructure**: Cloud-based automation handles complex sites reliably  
- **🔒 Built-in Features**: Automatic proxy rotation, CAPTCHA solving, and ad blocking
- **⚡ Better Performance**: Optimized cloud infrastructure for faster execution
- **🛡️ Security**: Isolated browser sessions prevent local system interference
- **💻 Cross-Platform**: Works on any system without browser dependencies
- **🤖 Integrated AI**: Built-in GPT-4o eliminates need for separate OpenAI API key

## Review Approaches

Choose between two analysis methods:

### 🚀 One-Shot Approach
- **Best for**: Quick overviews, initial assessments
- **How it works**: Single browser task reviews entire site in one go
- **Pros**: Faster execution, fewer API calls, good for sites with <10 pages
- **Cons**: Less detailed per-page analysis, may hit step/token limits on large sites

### 🔬 Multi-Step Approach (Recommended)
- **Best for**: Comprehensive analysis, detailed feedback
- **How it works**: Separate tasks for link discovery, individual page review, and overall analysis
- **Pros**: Detailed per-page insights, handles large sites better, more reliable
- **Cons**: Takes longer, more API calls

### 🕷️ Exhaustive Mode (Web Crawling)
- **Best for**: Complete site analysis, finding all documentation gaps
- **How it works**: Recursively discovers ALL pages by crawling the entire site, then reviews everything
- **Pros**: Finds every single page, comprehensive coverage analysis, identifies missing documentation
- **Cons**: Takes much longer, uses many more API calls, may hit safety limits on very large sites

```bash
# One-shot for quick assessment
python run_review.py --approach one-shot

# Multi-step for comprehensive review (default)
python run_review.py --approach multi-step

# Exhaustive crawling for complete site analysis
python run_review.py --exhaustive
```

## Live Automation Viewing

The tool automatically enables public sharing for all browser automation tasks, allowing you to watch the AI agent work in real-time:

- 🔗 **Public Share URLs**: Direct links to view automation execution  
- 📺 **Live Updates**: See the browser navigate, extract content, and analyze pages
- ⏱️ **Long-Running Tasks**: Tasks can take up to 15 minutes for comprehensive reviews
- 📱 **Any Device**: View automation from any browser, no login required

When you run a review, you'll see output like:
```
Task created: abc123...
🔗 Public share: https://browser-use.com/share/abc123...
📺 Live view: https://browser-use.com/live/abc123...
Status: running
```

## Usage

### Basic Usage

The script is pre-configured to review the Browser Use documentation:

```python
from docs_reviewer import DocumentationReviewer
import asyncio

async def review_docs():
    # API token can be set via environment variable or passed directly
    reviewer = DocumentationReviewer()
    
    # One-shot approach
    results = await reviewer.review_documentation_site(
        "https://docs.browser-use.com/introduction", 
        max_pages=10,
        approach="one-shot"
    )
    
    # Multi-step approach (default)
    results = await reviewer.review_documentation_site(
        "https://docs.browser-use.com/introduction", 
        max_pages=15,
        approach="multi-step"
    )
    
    print(f"Reviewed {results['total_pages_reviewed']} pages")

asyncio.run(review_docs())
```

### Command Line Examples

```bash
# Basic usage (defaults to Browser Use docs)
python run_review.py

# Review a specific site
python run_review.py https://docs.example.com

# Use one-shot approach for quick review
python run_review.py https://docs.example.com --approach one-shot

# Limit pages and use multi-step approach
python run_review.py https://docs.example.com --max-pages 20 --approach multi-step

# EXHAUSTIVE: Discover and review ALL pages (web crawling)
python run_review.py https://docs.example.com --exhaustive

# Exhaustive with safety limit (stops after finding 50 pages)
python run_review.py https://docs.example.com --exhaustive --max-pages 50

# Get help
python run_review.py --help
```

### Configuration Options

- `max_pages`: Maximum number of pages to review (default: 10-20 depending on approach)
- `approach`: Review method - "one-shot" or "multi-step" (default: "multi-step")  
- `browser_use_token`: Your Browser Use API token (includes AI analysis)

## Review Criteria

The AI reviewer evaluates each page based on:

### Content Quality (1-10)
- Clarity and readability
- Completeness of information
- Accuracy and up-to-date content
- Example quality and relevance

### Structure & Organization (1-10)
- Logical flow and hierarchy
- Proper heading structure
- Information architecture
- Content categorization

### User Experience (1-10)
- Navigation effectiveness
- Search functionality
- Breadcrumbs and wayfinding
- Mobile responsiveness
- Loading performance

### Technical Accuracy (1-10)
- Code examples correctness
- API documentation accuracy
- Implementation details
- Version consistency

## Output

The tool generates:

1. **Individual Page Reviews**: Detailed analysis of each page with scores and recommendations
2. **Overall Site Review**: Comprehensive site-wide analysis and strategic recommendations
3. **JSON Report**: Machine-readable output saved to `documentation_review_[timestamp].json`

### Sample Output

```
✅ Review completed!
📊 Pages reviewed: 12
📄 Full report saved to: documentation_review_1704123456.json
📈 Average score: 7.8/10
🎯 Score distribution: {'excellent (8-10)': 5, 'good (6-7)': 4, 'needs_improvement (4-5)': 2, 'poor (1-3)': 1, 'failed (0)': 0}

📋 Quick Summary:
  • Browser Use - Introduction: 9/10
  • Quick Start Guide: 8/10
  • API Reference: 7/10
  • Examples: 6/10
  • Advanced Usage: 8/10
  ... and 7 more pages
```

## Report Structure

The generated JSON report includes:

```json
{
  "start_url": "https://docs.browser-use.com/introduction",
  "total_pages_reviewed": 12,
  "page_reviews": [
    {
      "url": "...",
      "title": "...",
      "review": {
        "score": 8,
        "content_quality": {"score": 8, "feedback": "..."},
        "structure_organization": {"score": 7, "feedback": "..."},
        "user_experience": {"score": 9, "feedback": "..."},
        "technical_accuracy": {"score": 8, "feedback": "..."},
        "critical_issues": ["..."],
        "recommendations": ["..."],
        "positive_aspects": ["..."]
      }
    }
  ],
  "overall_review": {
    "statistics": {...},
    "site_analysis": "...",
    "priority_recommendations": ["..."]
  }
}
```

## Requirements

- Python 3.8+
- Browser Use API token (from [browser-use.com](https://browser-use.com))

## Dependencies

- `requests>=2.31.0` - HTTP requests for Browser Use Cloud API
- `python-dotenv>=1.0.0` - Environment variable management
- `beautifulsoup4>=4.12.0` - HTML parsing utilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
