#!/usr/bin/env python3
"""
AI-powered documentation reviewer using only Browser Use Cloud API.
Reviews documentation websites and provides critical feedback for improvements.
"""

import asyncio
import json
import os
import time
import requests
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentationReviewer:
    """AI agent that reviews documentation websites using only Browser Use Cloud API."""
    
    def __init__(self, browser_use_token: Optional[str] = None):
        """Initialize the documentation reviewer."""
        self.browser_use_token = browser_use_token or os.getenv("BROWSER_USE_API_TOKEN")
        
        if not self.browser_use_token:
            raise ValueError("Browser Use API token is required. Set BROWSER_USE_API_TOKEN environment variable.")
        
        self.api_base_url = os.getenv("BROWSER_USE_API_URL") or "https://api.browser-use.com/api/v1"
        
        # API session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.browser_use_token}",
            "Content-Type": "application/json"
        })
    
    async def review_documentation_site(self, start_url: str, max_pages: int = 50, approach: str = "multi-step", exhaustive: bool = False) -> Dict:
        """
        Review an entire documentation site starting from the given URL.
        
        Args:
            start_url: The starting URL of the documentation
            max_pages: Maximum number of pages to review (ignored in exhaustive mode)
            approach: "one-shot" or "multi-step" approach
            exhaustive: If True, recursively discovers and reviews ALL pages on the site
            
        Returns:
            Dictionary containing comprehensive review results
        """
        print(f"Starting documentation review for: {start_url}")
        print(f"Using {approach} approach")
        
        if exhaustive and approach == "one-shot":
            print("🚀 ONE-SHOT EXHAUSTIVE: AI will discover and review ALL pages in single task")
            print("⚠️  May take longer due to comprehensive site exploration")
            print(f"🛡️  Safety limit: {max_pages} pages maximum")
        elif exhaustive:
            print("🕷️  MULTI-STEP EXHAUSTIVE: Will crawl to discover ALL pages, then review each")
            print("⚠️  This may take significantly longer and use more API calls")
            print(f"🛡️  Safety limit: {max_pages} pages maximum")
        else:
            print(f"📊 Max pages: {max_pages}")
            
        print("⏱️  Note: Tasks can take up to 15 minutes to complete")
        print("🔗 Public share URLs will be displayed to watch automation live")
        print("="*50)
        
        if exhaustive and approach == "one-shot":
            # True one-shot exhaustive: AI does everything in one task
            print("🚀 One-shot exhaustive: AI will discover and review all pages in one task")
            return await self._one_shot_true_exhaustive_review(start_url, max_pages)
        elif exhaustive:
            # Multi-step exhaustive: crawl first, then review each page
            return await self._exhaustive_review(start_url, approach, max_pages)
        elif approach == "one-shot":
            return await self._one_shot_review(start_url, max_pages)
        else:
            return await self._multi_step_review(start_url, max_pages)
    
    async def _exhaustive_review(self, start_url: str, approach: str, safety_limit: int = 100) -> Dict:
        """Exhaustive review: Recursively discover and review ALL pages on the documentation site."""
        
        base_domain = urlparse(start_url).netloc
        discovered_urls = {start_url}  # All URLs we've found
        processed_urls = set()  # URLs we've extracted links from
        all_links = [start_url]  # Final list of URLs to review
        
        print("🕷️  Phase 1: Exhaustive link discovery (web crawling)")
        print(f"   Base domain: {base_domain}")
        
        # Crawl phase: Discover all URLs
        round_num = 1
        while discovered_urls - processed_urls:  # While there are unprocessed URLs
            unprocessed = list(discovered_urls - processed_urls)
            
            print(f"   Round {round_num}: Processing {len(unprocessed)} new URLs")
            print(f"   Total discovered so far: {len(discovered_urls)}")
            
            # Safety check to prevent infinite crawling
            if len(discovered_urls) > safety_limit:
                print(f"   ⚠️ Safety limit reached ({safety_limit} pages). Stopping discovery.")
                break
            
            # Process each unprocessed URL to find more links
            for url in unprocessed[:10]:  # Process max 10 URLs per round to avoid timeouts
                if url in processed_urls:
                    continue
                    
                print(f"     Crawling: {url}")
                try:
                    new_links = await self._extract_documentation_links(url)
                    new_count = 0
                    
                    for link in new_links:
                        if (link not in discovered_urls and 
                            base_domain in link and 
                            self._is_documentation_url(link)):
                            discovered_urls.add(link)
                            new_count += 1
                    
                    processed_urls.add(url)
                    print(f"       → Found {new_count} new URLs")
                    
                    # Brief pause to be respectful to the server
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"       ❌ Failed to crawl {url}: {e}")
                    processed_urls.add(url)
            
            round_num += 1
            
            # Safety check for rounds
            if round_num > 10:
                print("   ⚠️ Maximum crawling rounds reached. Stopping discovery.")
                break
        
        # Convert to final list
        all_links = list(discovered_urls)
        print(f"\n✅ Discovery complete! Found {len(all_links)} total pages")
        
        # Review phase: Review all discovered pages
        print(f"\n📊 Phase 2: Reviewing all {len(all_links)} discovered pages")
        
        # Multi-step exhaustive: review each discovered page individually
        return await self._multi_step_exhaustive_review(start_url, all_links)
    
    def _is_documentation_url(self, url: str) -> bool:
        """Check if a URL looks like a documentation page (not images, downloads, etc.)."""
        # Skip common non-documentation files
        skip_extensions = ['.pdf', '.zip', '.tar.gz', '.exe', '.dmg', '.png', '.jpg', '.gif', '.svg', '.css', '.js']
        skip_patterns = ['/api/download/', '/files/', '/assets/', '/static/', '/_next/', '/_nuxt/']
        
        url_lower = url.lower()
        
        # Skip if it has a non-documentation file extension
        for ext in skip_extensions:
            if url_lower.endswith(ext):
                return False
        
        # Skip if it matches non-documentation patterns
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
        
        # Skip if it's just an anchor link
        if '#' in url and url.split('#')[0] in url:
            return False
            
        return True
    
    async def _one_shot_true_exhaustive_review(self, start_url: str, max_pages_limit: int) -> Dict:
        """True one-shot exhaustive review: AI discovers and reviews everything in one task."""
        
        task_description = f"""
        TASK: Review the ENTIRE documentation website at {start_url}. You must visit multiple pages and review each one.

        STEP-BY-STEP INSTRUCTIONS:
        1. Go to {start_url}
        2. Read the page content thoroughly
        3. Review this page: rate content quality (1-10), structure (1-10), UX (1-10), technical accuracy (1-10)
        4. Look for navigation links to OTHER documentation pages
        5. Click on a documentation link to go to the next page
        6. Read and review this new page the same way
        7. Repeat: find more links, visit more pages, review each page
        8. Continue until you've reviewed at least 10+ documentation pages

        WHAT TO REVIEW FOR EACH PAGE:
        - Content clarity and usefulness
        - Page structure and organization
        - Navigation and user experience
        - Technical accuracy of information
        - Give each page an overall score 1-10

        IMPORTANT: 
        - Actually NAVIGATE to multiple pages (don't just stay on the first page)
        - REVIEW each page you visit
        - Look for links in: main navigation, sidebar, footer, "next" buttons
        - Stay on the same domain: {urlparse(start_url).netloc}

        SCORING CRITERIA (1-10 for each):
        - Content Quality: Clarity, completeness, accuracy, examples
        - Structure & Organization: Logical flow, hierarchy, findability  
        - User Experience: Navigation, search, mobile, performance
        - Technical Accuracy: Code examples, API docs, implementation details

        IMPORTANT: Save your complete analysis to a file named "review_results.json" with all the detailed results.

                 OUTPUT REQUIRED - Return this exact JSON format AND save to review_results.json:
         {{
             "total_pages_reviewed": <number of pages you actually visited and reviewed>,
             "page_reviews": [
                 {{
                     "url": "exact page URL",
                     "title": "page title you found",
                     "scores": {{
                         "overall": <1-10>,
                         "content_quality": <1-10>,
                         "structure_organization": <1-10>,
                         "user_experience": <1-10>,
                         "technical_accuracy": <1-10>
                     }},
                     "feedback": "Your detailed review of this page",
                     "critical_issues": ["issue 1", "issue 2"],
                     "recommendations": ["recommendation 1", "recommendation 2"]
                 }}
             ],
             "site_analysis": {{
                 "average_score": <calculated average of all page scores>,
                 "total_pages_discovered": <number of pages you found>,
                 "site_strengths": ["strength 1", "strength 2"],
                 "critical_site_issues": ["issue 1", "issue 2"],
                 "overall_assessment": "Your overall assessment of the documentation site"
             }}
         }}

                          CRITICAL REQUIREMENTS:
         - You MUST visit and review at least 5-10 different documentation pages
         - Actually CLICK on links to navigate to other pages  
         - Don't just stay on the first page - explore the documentation
         - Return valid JSON with the exact format above
         - Fill in ALL the fields in the JSON
         - Make sure "total_pages_reviewed" matches the number of pages in "page_reviews"

         EXAMPLE: Visit pages like /introduction, /quickstart, /api-reference, /guides, etc.
        """
        
        try:
            print(f"🚀 Starting true exhaustive one-shot review (max {max_pages_limit} pages)...")
            result = await self._run_browser_task(
                task_description, 
                max_steps=200,  # More steps for comprehensive discovery and review
                output_format="json"
            )
            
            print(f"🔍 Debug: Raw result type: {type(result)}")
            print(f"🔍 Debug: Raw result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print(f"🔍 Debug: Raw result preview: {str(result)[:500]}...")
            
            if result:
                result["review_approach"] = "exhaustive_one_shot"
                result["api_method"] = "Browser Use Cloud API (True Exhaustive One-Shot)"
                # Ensure required fields are present
                if "total_pages_reviewed" not in result:
                    result["total_pages_reviewed"] = result.get("total_pages_discovered", 1)
                if "total_pages_discovered" not in result:
                    result["total_pages_discovered"] = result.get("total_pages_reviewed", 1)
                return result
            else:
                print("❌ No result returned from AI task")
                return {
                    "error": "True exhaustive one-shot review failed - no result returned",
                    "review_approach": "exhaustive_one_shot",
                    "total_pages_discovered": 0,
                    "total_pages_reviewed": 0,
                    "page_reviews": [],
                    "site_analysis": {},
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            return {
                "error": f"True exhaustive one-shot review failed: {str(e)}",
                "review_approach": "exhaustive_one_shot",
                "total_pages_discovered": 0,
                "total_pages_reviewed": 0,
                "page_reviews": [],
                "site_analysis": {},
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    async def _one_shot_exhaustive_review(self, start_url: str, all_urls: List[str]) -> Dict:
        """One-shot review of all discovered URLs."""
        
        urls_text = "\n".join([f"- {url}" for url in all_urls[:50]])  # Limit for prompt size
        if len(all_urls) > 50:
            urls_text += f"\n... and {len(all_urls) - 50} more URLs"
        
        task_description = f"""
        You are an expert documentation reviewer. Review this ENTIRE documentation website comprehensively.

        DOCUMENTATION SITE: {start_url}
        TOTAL PAGES TO REVIEW: {len(all_urls)}

        ALL DISCOVERED PAGES:
        {urls_text}

        COMPREHENSIVE REVIEW TASK:
        1. Visit and analyze ALL the pages listed above
        2. For each page, evaluate content quality, structure, UX, and technical accuracy
        3. Look for site-wide patterns, consistency issues, and navigation problems
        4. Identify missing documentation, broken links, and gaps in coverage
        5. Provide detailed feedback for the entire documentation site

        SCORING CRITERIA (1-10 for each):
        - Content Quality: Clarity, completeness, accuracy, examples
        - Structure & Organization: Logical flow, hierarchy, findability  
        - User Experience: Navigation, search, mobile, performance
        - Technical Accuracy: Code examples, API docs, implementation details

        OUTPUT FORMAT:
        Return a comprehensive JSON report:
        {{
            "start_url": "{start_url}",
            "total_pages_discovered": {len(all_urls)},
            "total_pages_reviewed": <number>,
            "discovery_method": "exhaustive_crawling", 
            "page_reviews": [
                {{
                    "url": "page_url",
                    "title": "Page Title",
                    "scores": {{
                        "overall": <1-10>,
                        "content_quality": <1-10>,
                        "structure_organization": <1-10>,
                        "user_experience": <1-10>,
                        "technical_accuracy": <1-10>
                    }},
                    "feedback": {{
                        "content_quality": "specific feedback...",
                        "structure_organization": "specific feedback...",
                        "user_experience": "specific feedback...",
                        "technical_accuracy": "specific feedback..."
                    }},
                    "critical_issues": ["issue 1", "issue 2"],
                    "recommendations": ["rec 1", "rec 2"],
                    "positive_aspects": ["positive 1", "positive 2"]
                }}
            ],
            "site_analysis": {{
                "average_score": <number>,
                "score_distribution": {{}},
                "coverage_analysis": "assessment of documentation coverage",
                "navigation_effectiveness": "assessment of site navigation",
                "content_consistency": "assessment of consistency across pages",
                "missing_documentation": ["missing topic 1", "missing topic 2"],
                "site_strengths": ["strength 1", "strength 2"],
                "critical_site_issues": ["issue 1", "issue 2"],
                "priority_recommendations": ["rec 1", "rec 2"],
                "overall_assessment": "comprehensive site assessment"
            }}
        }}

        IMPORTANT:
        - Review ALL {len(all_urls)} pages discovered
        - Focus on comprehensive site-wide analysis
        - Identify documentation gaps and missing content
        - Provide actionable improvement recommendations
        - Ensure JSON is valid and complete
        """
        
        try:
            print("🚀 Starting exhaustive one-shot review...")
            result = await self._run_browser_task(
                task_description, 
                max_steps=200,  # More steps for comprehensive review
                output_format="json"
            )
            
            if result:
                result["review_approach"] = "exhaustive_one_shot"
                result["api_method"] = "Browser Use Cloud API (Exhaustive One-Shot)"
                result["total_pages_discovered"] = len(all_urls)
                # Ensure total_pages_reviewed is present
                if "total_pages_reviewed" not in result:
                    result["total_pages_reviewed"] = result.get("total_pages_discovered", len(all_urls))
                return result
            else:
                return {
                    "error": "Exhaustive one-shot review failed - no result returned",
                    "review_approach": "exhaustive_one_shot",
                    "total_pages_discovered": len(all_urls),
                    "total_pages_reviewed": 0,
                    "page_reviews": [],
                    "overall_review": {},
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            return {
                "error": f"Exhaustive one-shot review failed: {str(e)}",
                "review_approach": "exhaustive_one_shot",
                "total_pages_discovered": len(all_urls),
                "total_pages_reviewed": 0,
                "page_reviews": [],
                "overall_review": {},
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    async def _multi_step_exhaustive_review(self, start_url: str, all_urls: List[str]) -> Dict:
        """Multi-step review of all discovered URLs."""
        
        print(f"📊 Reviewing {len(all_urls)} pages individually...")
        page_reviews = []
        
        # Review each discovered page
        for i, url in enumerate(all_urls, 1):
            print(f"  Reviewing page {i}/{len(all_urls)}: {url}")
            try:
                review = await self._review_single_page(url)
                if review:
                    page_reviews.append(review)
                await asyncio.sleep(1)  # Be respectful to the API
            except Exception as e:
                print(f"  ❌ Failed to review {url}: {e}")
                page_reviews.append({
                    "url": url,
                    "error": str(e),
                    "scores": {"overall": 0}
                })
        
        # Generate comprehensive overall analysis
        print("📈 Generating comprehensive site analysis...")
        overall_review = await self._generate_exhaustive_overall_analysis(page_reviews, start_url, len(all_urls))
        
        return {
            "start_url": start_url,
            "review_approach": "exhaustive_multi_step",
            "api_method": "Browser Use Cloud API (Exhaustive Multi-Step)",
            "total_pages_discovered": len(all_urls),
            "total_pages_reviewed": len(page_reviews),
            "page_reviews": page_reviews,
            "overall_review": overall_review,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    async def _one_shot_review(self, start_url: str, max_pages: int) -> Dict:
        """One-shot approach: Ask Browser Use API to review entire documentation site in one task."""
        
        task_description = f"""
        You are an expert documentation reviewer. Your task is to comprehensively review the documentation website starting at {start_url}.

        TASK OVERVIEW:
        1. Navigate to {start_url}
        2. Discover and visit up to {max_pages} documentation pages on the same domain
        3. For each page, analyze content quality, structure, user experience, and technical accuracy
        4. Provide detailed feedback and scoring for each page
        5. Generate an overall site review with recommendations

        REVIEW CRITERIA FOR EACH PAGE:
        - Content Quality (1-10): Clarity, completeness, accuracy, examples quality
        - Structure & Organization (1-10): Logical flow, heading hierarchy, categorization
        - User Experience (1-10): Navigation, search, breadcrumbs, mobile responsiveness
        - Technical Accuracy (1-10): Code examples, API docs, implementation details

        IMPORTANT: Save your complete analysis to a file named "review_results.json" with all the detailed results.

        OUTPUT FORMAT:
        Return a comprehensive JSON report with this structure AND save to review_results.json:
        {{
            "start_url": "{start_url}",
            "review_approach": "one-shot",
            "total_pages_reviewed": <number>,
            "page_reviews": [
                {{
                    "url": "page_url",
                    "title": "Page Title",
                    "scores": {{
                        "overall": <1-10>,
                        "content_quality": <1-10>,
                        "structure_organization": <1-10>,
                        "user_experience": <1-10>,
                        "technical_accuracy": <1-10>
                    }},
                    "feedback": {{
                        "content_quality": "detailed feedback...",
                        "structure_organization": "detailed feedback...",
                        "user_experience": "detailed feedback...",
                        "technical_accuracy": "detailed feedback..."
                    }},
                    "critical_issues": ["issue 1", "issue 2"],
                    "recommendations": ["rec 1", "rec 2"],
                    "positive_aspects": ["positive 1", "positive 2"]
                }}
            ],
            "overall_review": {{
                "average_score": <number>,
                "score_distribution": {{
                    "excellent (8-10)": <count>,
                    "good (6-7)": <count>,
                    "needs_improvement (4-5)": <count>,
                    "poor (1-3)": <count>
                }},
                "site_strengths": ["strength 1", "strength 2"],
                "critical_site_issues": ["issue 1", "issue 2"],
                "priority_recommendations": ["rec 1", "rec 2"],
                "overall_assessment": "detailed overall assessment..."
            }},
            "timestamp": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
        }}

        IMPORTANT INSTRUCTIONS:
        - Focus on internal documentation pages only (same domain as {start_url})
        - Skip navigation, footer, and external links
        - Provide constructive, actionable feedback
        - Be critical but fair in your assessments
        - Ensure JSON output is valid and properly formatted
        - Save complete results to "review_results.json" file
        - Limit to {max_pages} pages maximum to stay within step limits
        """
        
        try:
            print("🚀 Starting one-shot documentation review...")
            result = await self._run_browser_task(
                task_description, 
                max_steps=150,  # More steps for comprehensive review
                output_format="json"
            )
            
            if result:
                result["review_approach"] = "one-shot"
                result["api_method"] = "Browser Use Cloud API (One-Shot)"
                return result
            else:
                return {
                    "error": "One-shot review failed - no result returned",
                    "review_approach": "one-shot",
                    "total_pages_reviewed": 0,
                    "page_reviews": [],
                    "overall_review": {},
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            return {
                "error": f"One-shot review failed: {str(e)}",
                "review_approach": "one-shot",
                "total_pages_reviewed": 0,
                "page_reviews": [],
                "overall_review": {},
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    async def _multi_step_review(self, start_url: str, max_pages: int) -> Dict:
        """Multi-step approach: First get all links, then review each page individually."""
        
        # Step 1: Extract documentation links
        print("📋 Step 1: Extracting documentation links...")
        try:
            links = await self._extract_documentation_links(start_url)
        except Exception as e:
            print(f"❌ Failed to extract links: {e}")
            return {
                "error": f"Failed to extract documentation links: {str(e)}",
                "review_approach": "multi-step",
                "total_pages_reviewed": 0,
                "page_reviews": [],
                "overall_review": {},
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        if not links:
            print("⚠️ No additional links found, will review start page only")
            links = []
        
        # Include the start URL and limit pages
        all_links = list(set([start_url] + links))[:max_pages]
        print(f"Found {len(links)} links, reviewing {len(all_links)} pages total")
        
        # Step 2: Review each page
        print("📊 Step 2: Reviewing individual pages...")
        page_reviews = []
        
        for i, url in enumerate(all_links, 1):
            print(f"  Reviewing page {i}/{len(all_links)}: {url}")
            try:
                review = await self._review_single_page(url)
                if review:
                    page_reviews.append(review)
                await asyncio.sleep(1)  # Be respectful to the API
            except Exception as e:
                print(f"  ❌ Failed to review {url}: {e}")
                page_reviews.append({
                    "url": url,
                    "error": str(e),
                    "scores": {"overall": 0}
                })
        
        # Step 3: Generate overall analysis
        print("📈 Step 3: Generating overall site analysis...")
        overall_review = await self._generate_overall_analysis(page_reviews, start_url)
        
        return {
            "start_url": start_url,
            "review_approach": "multi-step",
            "api_method": "Browser Use Cloud API (Multi-Step)",
            "total_pages_reviewed": len(page_reviews),
            "page_reviews": page_reviews,
            "overall_review": overall_review,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    async def _extract_documentation_links(self, start_url: str) -> List[str]:
        """Extract all documentation links from the starting page."""
        
        base_domain = urlparse(start_url).netloc
        
        task_description = f"""
        Visit {start_url} and extract ALL internal documentation links comprehensively.
        
        COMPREHENSIVE LINK DISCOVERY:
        1. Navigate to {start_url}
        2. Look for links in multiple locations:
           - Main navigation menu (nav, .nav, .navigation)
           - Sidebar navigation (.sidebar, .menu, aside)
           - Footer documentation links
           - Breadcrumb navigation
           - Table of contents
           - "See also" or "Related" sections
           - Dropdown menus and expandable sections
        3. Find ALL internal links to pages on the same domain ({base_domain})
        4. Include both visible and hidden/dropdown navigation links
        5. Filter out non-documentation content:
           - Images, downloads, assets (.png, .jpg, .pdf, .zip)
           - API endpoints (/api/, /download/)
           - Static resources (/static/, /_next/, /assets/)
        6. Include documentation pages, guides, tutorials, API docs, examples
        
        IMPORTANT: Be thorough! Many documentation sites hide links in:
        - Collapsible navigation sections
        - Dropdown menus that need to be expanded
        - Secondary navigation areas
        - Mobile navigation menus
        
        Return a comprehensive JSON array of ALL documentation URLs found:
        {{
            "links": [
                "https://{base_domain}/docs/getting-started",
                "https://{base_domain}/api/reference", 
                "https://{base_domain}/guides/tutorial",
                "https://{base_domain}/examples/basic"
            ]
        }}
        
        Target: Find AT LEAST 10-20 documentation pages if they exist on this site.
        """
        
        try:
            result = await self._run_browser_task(task_description, max_steps=10, output_format="json")
            
            if result and "links" in result:
                # Filter and validate links
                valid_links = []
                for link in result["links"]:
                    if (link.startswith(f"http://{base_domain}") or 
                        link.startswith(f"https://{base_domain}")) and "#" not in link:
                        valid_links.append(link)
                return valid_links[:50]  # Limit to reasonable number
            
            return []
            
        except Exception as e:
            print(f"Error extracting links: {e}")
            print("🔄 Trying simpler link extraction...")
            try:
                return await self._simple_link_extraction(start_url)
            except Exception as e2:
                print(f"Simple extraction also failed: {e2}")
                print("⚠️ Proceeding with just the start URL")
                return []
    
    async def _simple_link_extraction(self, start_url: str) -> List[str]:
        """Fallback simple link extraction with fewer steps."""
        base_domain = urlparse(start_url).netloc
        
        simple_task = f"""
        Go to {start_url} and find ALL navigation and documentation links.
        
        SIMPLIFIED BUT THOROUGH SEARCH:
        1. Main navigation menu - click/expand any dropdowns
        2. Sidebar navigation - expand collapsible sections  
        3. Footer documentation links
        4. Any "Documentation", "Guides", "API", "Tutorial" links
        5. Breadcrumb navigation
        
        Be sure to click on expandable navigation elements to reveal hidden links!
        
        Return ALL internal documentation links from {base_domain}:
        {{"links": ["url1", "url2", "url3", "url4", "url5"]}}
        
        Goal: Find at least 5-10 documentation pages.
        """
        
        try:
            result = await self._run_browser_task(simple_task, max_steps=100, output_format="json")
            if result and "links" in result:
                valid_links = []
                for link in result["links"][:10]:  # Limit to 10 links
                    if base_domain in str(link) and "#" not in str(link):
                        valid_links.append(str(link))
                return valid_links
        except Exception as e:
            print(f"Simple extraction also failed: {e}")
        
        return []
    
    def _extract_json_from_text(self, text: str) -> Dict:
        """Extract JSON from text that might contain other content."""
        if not text:
            return {"raw_output": "No output"}
        
        # Try to find JSON in the text
        import re
        
        # Look for JSON objects starting with { and ending with }
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
        
        # If no JSON found, return raw text
        return {"raw_output": text.strip()}
    
    async def _get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get task details including share URLs using the GET task API."""
        try:
            response = self.session.get(f"{self.api_base_url}/task/{task_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"    ⚠️ Could not fetch task details: {response.status_code}")
                return None
        except Exception as e:
            print(f"    ⚠️ Error fetching task details: {e}")
            return None
    
    async def _get_task_status(self, task_id: str) -> Optional[str]:
        """Get just the task status using the lightweight status API."""
        try:
            response = self.session.get(f"{self.api_base_url}/task/{task_id}/status")
            if response.status_code == 200:
                return response.json()  # Returns just the status string
            else:
                return None
        except Exception as e:
            return None
    
    async def _review_single_page(self, url: str) -> Dict:
        """Review a single documentation page."""
        
        task_description = f"""
        You are an expert documentation reviewer. Analyze the documentation page at {url} and provide detailed feedback.

        ANALYSIS REQUIREMENTS:
        1. Navigate to {url}
        2. Extract key page information (title, content structure, elements)
        3. Evaluate the page across these criteria:
           - Content Quality: Clarity, completeness, accuracy, examples
           - Structure & Organization: Logical flow, heading hierarchy
           - User Experience: Navigation, search, accessibility
           - Technical Accuracy: Code examples, API docs, implementation details

        OUTPUT FORMAT:
        Return a JSON object with this structure:
        {{
            "url": "{url}",
            "title": "extracted page title",
            "word_count": <estimated word count>,
            "has_navigation": <true/false>,
            "has_search": <true/false>,
            "has_breadcrumbs": <true/false>,
            "code_blocks_count": <number>,
            "scores": {{
                "overall": <1-10>,
                "content_quality": <1-10>,
                "structure_organization": <1-10>,
                "user_experience": <1-10>,
                "technical_accuracy": <1-10>
            }},
            "feedback": {{
                "content_quality": "specific feedback on content quality...",
                "structure_organization": "specific feedback on structure...",
                "user_experience": "specific feedback on UX...",
                "technical_accuracy": "specific feedback on technical aspects..."
            }},
            "critical_issues": ["specific issue 1", "specific issue 2"],
            "recommendations": ["specific recommendation 1", "specific recommendation 2"],
            "positive_aspects": ["what works well 1", "what works well 2"]
        }}

        Be specific and actionable in your feedback. Focus on concrete improvements.
        """
        
        try:
            result = await self._run_browser_task(task_description, max_steps=20, output_format="json")
            
            # Handle partial results from stopped tasks
            if isinstance(result, dict) and result.get("partial_result"):
                print(f"    ⚠️ Partial results for {url}")
                return {
                    "url": url,
                    "warning": "Task was stopped - partial results",
                    "scores": {"overall": 5}  # Neutral score for partial results
                }
            
            return result
            
        except Exception as e:
            return {
                "url": url,
                "error": f"Failed to review page: {str(e)}",
                "scores": {"overall": 0}
            }
    
    async def _generate_overall_analysis(self, page_reviews: List[Dict], start_url: str) -> Dict:
        """Generate overall site analysis based on individual page reviews."""
        
        # Calculate statistics
        scores = []
        all_issues = []
        all_recommendations = []
        all_positives = []
        
        for review in page_reviews:
            if "scores" in review and "overall" in review["scores"]:
                scores.append(review["scores"]["overall"])
            if "critical_issues" in review:
                all_issues.extend(review["critical_issues"])
            if "recommendations" in review:
                all_recommendations.extend(review["recommendations"])
            if "positive_aspects" in review:
                all_positives.extend(review["positive_aspects"])
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        score_distribution = {
            "excellent (8-10)": len([s for s in scores if s >= 8]),
            "good (6-7)": len([s for s in scores if 6 <= s < 8]),
            "needs_improvement (4-5)": len([s for s in scores if 4 <= s < 6]),
            "poor (1-3)": len([s for s in scores if 1 <= s < 4])
        }
        
        task_description = f"""
        You are a documentation strategist. Analyze this comprehensive review data for {start_url} and provide strategic recommendations.

        REVIEW DATA:
        - Total pages reviewed: {len(page_reviews)}
        - Average score: {avg_score:.2f}/10
        - Score distribution: {score_distribution}
        - Common issues found: {list(set(all_issues))[:20]}
        - Common recommendations: {list(set(all_recommendations))[:20]}
        - Positive aspects: {list(set(all_positives))[:20]}

        INDIVIDUAL PAGE SCORES:
        {[{"url": r.get("url", ""), "title": r.get("title", ""), "score": r.get("scores", {}).get("overall", 0)} for r in page_reviews[:10]]}

        Provide strategic analysis in this JSON format:
        {{
            "average_score": {avg_score:.2f},
            "score_distribution": {score_distribution},
            "site_strengths": ["strength 1", "strength 2", "strength 3"],
            "critical_site_issues": ["critical issue 1", "critical issue 2"],
            "priority_recommendations": ["high priority rec 1", "high priority rec 2"],
            "content_consistency": "assessment of content consistency across pages",
            "navigation_assessment": "assessment of site navigation and structure",
            "technical_documentation_quality": "assessment of technical docs quality",
            "user_experience_summary": "overall UX assessment",
            "overall_assessment": "comprehensive strategic assessment and next steps"
        }}

        Focus on site-wide patterns and strategic improvements rather than page-specific details.
        """
        
        try:
            result = await self._run_browser_task(task_description, max_steps=20, output_format="json")
            if result:
                # Handle partial results from stopped tasks
                if isinstance(result, dict) and result.get("partial_result"):
                    print("    ⚠️ Overall analysis was partially completed")
                    result["note"] = "Analysis was stopped before completion"
                return result
        except Exception as e:
            print(f"Error generating overall analysis: {e}")
        
        # Fallback analysis
        return {
            "average_score": round(avg_score, 2),
            "score_distribution": score_distribution,
            "site_strengths": list(set(all_positives))[:5],
            "critical_site_issues": list(set(all_issues))[:5],
            "priority_recommendations": list(set(all_recommendations))[:5],
            "overall_assessment": f"Analyzed {len(page_reviews)} pages with an average score of {avg_score:.1f}/10",
            "note": "Fallback analysis used due to API issues"
        }
    
    async def _generate_exhaustive_overall_analysis(self, page_reviews: List[Dict], start_url: str, total_discovered: int) -> Dict:
        """Generate comprehensive analysis for exhaustive review with coverage insights."""
        
        # Calculate statistics
        scores = []
        all_issues = []
        all_recommendations = []
        all_positives = []
        
        for review in page_reviews:
            if "scores" in review and "overall" in review["scores"]:
                scores.append(review["scores"]["overall"])
            if "critical_issues" in review:
                all_issues.extend(review["critical_issues"])
            if "recommendations" in review:
                all_recommendations.extend(review["recommendations"])
            if "positive_aspects" in review:
                all_positives.extend(review["positive_aspects"])
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        score_distribution = {
            "excellent (8-10)": len([s for s in scores if s >= 8]),
            "good (6-7)": len([s for s in scores if 6 <= s < 8]),
            "needs_improvement (4-5)": len([s for s in scores if 4 <= s < 6]),
            "poor (1-3)": len([s for s in scores if 1 <= s < 4])
        }
        
        # Enhanced analysis for exhaustive review
        task_description = f"""
        You are a documentation strategist analyzing a COMPREHENSIVE review of an entire documentation website.

        EXHAUSTIVE REVIEW DATA for {start_url}:
        - Total pages discovered by web crawling: {total_discovered}
        - Total pages successfully reviewed: {len(page_reviews)}
        - Coverage: {len(page_reviews)/total_discovered*100:.1f}%
        - Average score: {avg_score:.2f}/10
        - Score distribution: {score_distribution}

        COMPREHENSIVE SITE ANALYSIS:
        - All discovered issues: {list(set(all_issues))[:30]}
        - All recommendations: {list(set(all_recommendations))[:30]}
        - Positive aspects: {list(set(all_positives))[:30]}

        SAMPLE PAGE SCORES (first 20):
        {[{"url": r.get("url", ""), "title": r.get("title", ""), "score": r.get("scores", {}).get("overall", 0)} for r in page_reviews[:20]]}

        Provide a STRATEGIC ANALYSIS for this COMPLETE documentation site in JSON format. store all the results in filenamed review_results.json:
        {{
            "coverage_analysis": {{
                "total_pages_discovered": {total_discovered},
                "total_pages_reviewed": {len(page_reviews)},
                "coverage_percentage": {len(page_reviews)/total_discovered*100:.1f},
                "missing_pages_analysis": "analysis of what pages couldn't be reviewed",
                "site_completeness": "assessment of how comprehensive the documentation is"
            }},
            "average_score": {avg_score:.2f},
            "score_distribution": {score_distribution},
            "content_gaps": {{
                "missing_topics": ["topic 1", "topic 2"],
                "incomplete_sections": ["section 1", "section 2"],
                "outdated_content": ["area 1", "area 2"]
            }},
            "site_architecture": {{
                "navigation_effectiveness": "assessment of site navigation",
                "information_architecture": "assessment of content organization",
                "user_journey_analysis": "how well users can find information",
                "search_and_discoverability": "assessment of search and findability"
            }},
            "consistency_analysis": {{
                "content_style": "assessment of writing consistency",
                "formatting_consistency": "assessment of visual consistency", 
                "technical_accuracy_consistency": "assessment of technical info consistency"
            }},
            "site_strengths": ["strength 1", "strength 2", "strength 3"],
            "critical_site_issues": ["critical issue 1", "critical issue 2"],
            "strategic_recommendations": {{
                "immediate_fixes": ["fix 1", "fix 2"],
                "short_term_improvements": ["improvement 1", "improvement 2"],
                "long_term_strategy": ["strategy 1", "strategy 2"]
            }},
            "competitive_positioning": "how this documentation compares to industry standards",
            "overall_assessment": "comprehensive strategic assessment and roadmap"
        }}

        Focus on STRATEGIC insights from this COMPLETE site analysis. Consider the full scope of {total_discovered} pages discovered.
        """
        
        try:
            result = await self._run_browser_task(task_description, max_steps=25, output_format="json")
            if result:
                # Handle partial results from stopped tasks
                if isinstance(result, dict) and result.get("partial_result"):
                    print("    ⚠️ Exhaustive analysis was partially completed")
                    result["note"] = "Analysis was stopped before completion"
                return result
        except Exception as e:
            print(f"Error generating exhaustive analysis: {e}")
        
        # Enhanced fallback analysis for exhaustive review
        return {
            "coverage_analysis": {
                "total_pages_discovered": total_discovered,
                "total_pages_reviewed": len(page_reviews),
                "coverage_percentage": round(len(page_reviews)/total_discovered*100, 1) if total_discovered > 0 else 0,
                "site_completeness": f"Discovered {total_discovered} pages through exhaustive crawling"
            },
            "average_score": round(avg_score, 2),
            "score_distribution": score_distribution,
            "site_strengths": list(set(all_positives))[:10],  # More insights for exhaustive
            "critical_site_issues": list(set(all_issues))[:10],
            "strategic_recommendations": {
                "immediate_fixes": list(set(all_recommendations))[:5],
                "long_term_strategy": ["Consider comprehensive documentation audit", "Implement consistent style guide"]
            },
            "overall_assessment": f"EXHAUSTIVE ANALYSIS: Crawled and analyzed {len(page_reviews)} of {total_discovered} discovered pages with average score of {avg_score:.1f}/10",
            "note": "Fallback analysis used due to API issues - based on exhaustive crawling data"
        }
    
    async def _run_browser_task(self, task_description: str, max_steps: int = 50, output_format: str = "json") -> Dict:
        """Run a task using Browser Use Cloud API."""
        
        payload = {
            "task": task_description,
            "llm_model": "gpt-4.1-mini",  # Use the most capable model
            "max_agent_steps": max_steps,
            "use_adblock": True,
            "use_proxy": True,
            "highlight_elements": True,
            "enable_public_share": True,  # Enable public sharing to view automation
            "browser_profile": "default",
        }
        
        # Create task
        response = self.session.post(f"{self.api_base_url}/run-task", json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Failed to create task: {response.status_code} - {response.text}")
        
        task_data = response.json()
        task_id = task_data.get("id")
        
        if not task_id:
            raise Exception("No task ID returned from API")
        
        print(f"    Task created: {task_id}")
        
        # Get task details to fetch share URLs
        await asyncio.sleep(5)  # Wait for task to initialize and URLs to be available
        task_details = await self._get_task_details(task_id)
        
        if task_details:
            if task_details.get("public_share_url"):
                print(f"    🔗 Public share: {task_details['public_share_url']}")
            if task_details.get("live_url"):
                print(f"    📺 Live view: {task_details['live_url']}")
            print(f"    ⏱️ Status: {task_details.get('status', 'unknown')}")
        else:
            print(f"    🔗 Task ID: {task_id} (share URLs will be available once task starts)")
        
        # Poll for completion
        max_wait_time = 3600  # 1 hour max
        wait_interval = 15  # Check every 15 seconds
        elapsed_time = 0
        
        share_urls_shown = False
        
        while elapsed_time < max_wait_time:
            # Use lightweight status endpoint for polling
            status = await self._get_task_status(task_id)
            
            if not status:
                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval
                continue
            
            print(f"    Status: {status}")
            
            # Get full task details when running to show share URLs
            if not share_urls_shown and status in ["running", "in_progress"]:
                task_details = await self._get_task_details(task_id)
                if task_details:
                    if task_details.get("public_share_url"):
                        print(f"    🔗 Public share: {task_details['public_share_url']}")
                    if task_details.get("live_url"):
                        print(f"    📺 Live view: {task_details['live_url']}")
                    share_urls_shown = True
            
            if status in ["completed", "finished", "stopped"]:
                # Task is done - get full task details to retrieve output
                print(f"    Task {status}. Retrieving results...")
                
                task_details = await self._get_task_details(task_id)
                if not task_details:
                    return {"error": "Could not retrieve task details after completion"}
                
                # Download all available files from the task
                try:
                    downloaded_files = await self.download_all_task_files(task_id)
                except Exception as e:
                    print(f"    ⚠️ Error downloading task files: {e}")
                    downloaded_files = {}
                
                # First try to get output from the task data itself
                if task_details.get("output"):
                    try:
                        if isinstance(task_details["output"], str):
                            # Try to parse as JSON first
                            result = json.loads(task_details["output"])
                        else:
                            result = task_details["output"]
                        
                        # Add downloaded files info to result
                        if downloaded_files:
                            result["downloaded_files"] = downloaded_files
                        return result
                    except json.JSONDecodeError:
                        # If not valid JSON, try to extract JSON from the text
                        result = self._extract_json_from_text(str(task_details["output"]))
                        if downloaded_files:
                            result["downloaded_files"] = downloaded_files
                        return result
                
                # Try to get output file
                output_response = self.session.get(f"{self.api_base_url}/get-task-output-file/{task_id}")
                
                if output_response.status_code == 200:
                    try:
                        result = output_response.json()
                        if downloaded_files:
                            result["downloaded_files"] = downloaded_files
                        return result
                    except json.JSONDecodeError:
                        # Try to extract JSON from text response
                        result = self._extract_json_from_text(output_response.text)
                        if downloaded_files:
                            result["downloaded_files"] = downloaded_files
                        return result
                
                # If no output available but task is done
                if status == "stopped":
                    print("    ⚠️ Task was stopped - may have partial results")
                    result = {"warning": "Task was stopped before completion", "partial_result": True}
                    if downloaded_files:
                        result["downloaded_files"] = downloaded_files
                    return result
                
                # Fallback to any available data
                result = task_details.get("result", {"message": f"Task {status} but no output available"})
                if downloaded_files:
                    result["downloaded_files"] = downloaded_files
                return result
            
            elif status == "failed":
                # Get full task details to see error message
                task_details = await self._get_task_details(task_id)
                error = task_details.get("error", "Unknown error") if task_details else "Unknown error"
                raise Exception(f"Task failed: {error}")
            
            # Wait before next check
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        raise Exception(f"Task timed out after {max_wait_time} seconds")
    
    def check_and_display_results_file(self):
        """Check for review_results.json file and display its contents if it exists."""
        results_file = "review_results.json"
        
        if os.path.exists(results_file):
            print(f"\n🎯 Found output file: {results_file}")
            print("="*60)
            
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    file_content = json.load(f)
                
                print("📋 Contents of review_results.json:")
                print(json.dumps(file_content, indent=2, ensure_ascii=False))
                print("="*60)
                
                return file_content
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON file: {e}")
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        raw_content = f.read()
                    print("📄 Raw file contents:")
                    print(raw_content)
                    print("="*60)
                except Exception as read_error:
                    print(f"❌ Error reading file: {read_error}")
                    
            except Exception as e:
                print(f"❌ Error reading {results_file}: {e}")
        else:
            print(f"\n📄 No {results_file} file found in current directory")
            
        return None
    
    def merge_results_with_file(self, results: Dict) -> Dict:
        """Merge the main results with review_results.json file if it exists."""
        results_file = "review_results.json"
        
        # Also check for the file in downloaded files
        downloaded_files = results.get("downloaded_files", {})
        review_file_path = None
        
        # Look for review_results.json in multiple locations
        if os.path.exists(results_file):
            review_file_path = results_file
        else:
            # Check in downloaded files
            for file_type, filepath in downloaded_files.items():
                if "review_results.json" in filepath:
                    if os.path.exists(filepath):
                        review_file_path = filepath
                        break
        
        if review_file_path:
            try:
                with open(review_file_path, 'r', encoding='utf-8') as f:
                    file_content = json.load(f)
                
                print(f"\n🔗 Merging results from {review_file_path}")
                
                # Merge the file content into the results
                # Prioritize file content for detailed analysis while keeping main results structure
                merged_results = results.copy()
                
                # Add file content as a special section
                merged_results["ai_generated_file"] = file_content
                
                # Try to merge key fields intelligently
                if isinstance(file_content, dict):
                    # PRIORITY: Use page reviews from file if they exist and are comprehensive
                    if "page_reviews" in file_content and isinstance(file_content["page_reviews"], list):
                        if len(file_content["page_reviews"]) > len(merged_results.get("page_reviews", [])):
                            # File has more comprehensive page reviews, use those
                            merged_results["page_reviews"] = file_content["page_reviews"]
                            print(f"✅ Using {len(file_content['page_reviews'])} page reviews from AI file")
                        else:
                            # Merge both sets
                            if "page_reviews" not in merged_results:
                                merged_results["page_reviews"] = []
                            
                            existing_urls = {page.get("url") for page in merged_results.get("page_reviews", [])}
                            for page_review in file_content["page_reviews"]:
                                if page_review.get("url") not in existing_urls:
                                    merged_results["page_reviews"].append(page_review)
                    
                    # Merge site analysis if available
                    if "site_analysis" in file_content:
                        merged_results["enhanced_site_analysis"] = file_content["site_analysis"]
                        # Also copy to overall_review if it doesn't exist
                        if "overall_review" not in merged_results:
                            merged_results["overall_review"] = file_content["site_analysis"]
                    
                    # PRIORITY: Use totals from file if they're higher (more accurate)
                    if "total_pages_reviewed" in file_content and file_content["total_pages_reviewed"]:
                        current_total = merged_results.get("total_pages_reviewed", 0)
                        file_total = file_content["total_pages_reviewed"]
                        if file_total > current_total:
                            merged_results["total_pages_reviewed"] = file_total
                            print(f"✅ Updated total_pages_reviewed from {current_total} to {file_total}")
                    
                    if "total_pages_discovered" in file_content and file_content["total_pages_discovered"]:
                        current_total = merged_results.get("total_pages_discovered", 0)
                        file_total = file_content["total_pages_discovered"]
                        if file_total > current_total:
                            merged_results["total_pages_discovered"] = file_total
                            print(f"✅ Updated total_pages_discovered from {current_total} to {file_total}")
                    
                    # Add any additional analysis from the file
                    for key, value in file_content.items():
                        if key not in merged_results and key not in ["page_reviews", "site_analysis"]:
                            merged_results[f"ai_file_{key}"] = value
                
                merged_results["has_ai_generated_file"] = True
                print(f"✅ Successfully merged data from {review_file_path}")
                return merged_results
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Could not parse {review_file_path}: {e}")
                results["ai_file_error"] = f"JSON parsing error: {str(e)}"
                return results
            except Exception as e:
                print(f"⚠️ Error reading {review_file_path}: {e}")
                results["ai_file_error"] = f"File reading error: {str(e)}"
                return results
        else:
            print(f"\n📄 No review_results.json file found - using standard results")
            results["has_ai_generated_file"] = False
            return results
    
    async def download_all_task_files(self, task_id: str) -> Dict[str, str]:
        """Download all available files from a Browser Use API task."""
        print(f"\n📥 Downloading all available files for task {task_id}...")
        downloaded_files = {}
        
        # Create downloads directory
        downloads_dir = f"task_{task_id}_files"
        os.makedirs(downloads_dir, exist_ok=True)
        print(f"📁 Files will be saved to: {downloads_dir}/")
        
        # 1. Try to download screenshots
        try:
            print("📸 Checking for screenshots...")
            response = self.session.get(f"{self.api_base_url}/task/{task_id}/screenshots")
            if response.status_code == 200:
                screenshots_data = response.json()
                if isinstance(screenshots_data, list) and screenshots_data:
                    print(f"   Found {len(screenshots_data)} screenshots")
                    for i, screenshot_url in enumerate(screenshots_data):
                        screenshot_response = requests.get(screenshot_url)
                        if screenshot_response.status_code == 200:
                            filename = f"screenshot_{i+1}.png"
                            filepath = os.path.join(downloads_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(screenshot_response.content)
                            downloaded_files[f"screenshot_{i+1}"] = filepath
                            print(f"   ✅ Downloaded: {filename}")
                elif isinstance(screenshots_data, dict) and screenshots_data.get('screenshots'):
                    # Handle different response format
                    screenshots = screenshots_data['screenshots']
                    print(f"   Found {len(screenshots)} screenshots")
                    for i, screenshot_url in enumerate(screenshots):
                        screenshot_response = requests.get(screenshot_url)
                        if screenshot_response.status_code == 200:
                            filename = f"screenshot_{i+1}.png"
                            filepath = os.path.join(downloads_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(screenshot_response.content)
                            downloaded_files[f"screenshot_{i+1}"] = filepath
                            print(f"   ✅ Downloaded: {filename}")
                else:
                    print("   📸 No screenshots available")
            else:
                print(f"   ⚠️ Screenshots endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading screenshots: {e}")
        
        # 2. Try to download GIF recording
        try:
            print("🎬 Checking for GIF recording...")
            response = self.session.get(f"{self.api_base_url}/task/{task_id}/gif")
            if response.status_code == 200:
                gif_data = response.json()
                if gif_data.get('download_url'):
                    gif_response = requests.get(gif_data['download_url'])
                    if gif_response.status_code == 200:
                        filename = "automation_recording.gif"
                        filepath = os.path.join(downloads_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(gif_response.content)
                        downloaded_files["gif_recording"] = filepath
                        print(f"   ✅ Downloaded: {filename}")
                    else:
                        print(f"   ⚠️ GIF download failed: {gif_response.status_code}")
                else:
                    print("   🎬 No GIF recording available")
            else:
                print(f"   ⚠️ GIF endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading GIF: {e}")
        
        # 3. Try to download media files
        try:
            print("🎥 Checking for media files...")
            response = self.session.get(f"{self.api_base_url}/task/{task_id}/media")
            if response.status_code == 200:
                media_data = response.json()
                if isinstance(media_data, list) and media_data:
                    print(f"   Found {len(media_data)} media files")
                    for i, media_url in enumerate(media_data):
                        media_response = requests.get(media_url)
                        if media_response.status_code == 200:
                            # Try to determine file extension from URL or content-type
                            content_type = media_response.headers.get('content-type', '')
                            if 'video' in content_type:
                                ext = '.mp4'
                            elif 'image' in content_type:
                                ext = '.png'
                            else:
                                ext = '.bin'
                            
                            filename = f"media_{i+1}{ext}"
                            filepath = os.path.join(downloads_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(media_response.content)
                            downloaded_files[f"media_{i+1}"] = filepath
                            print(f"   ✅ Downloaded: {filename}")
                elif isinstance(media_data, dict) and media_data.get('media_files'):
                    # Handle different response format
                    media_files = media_data['media_files']
                    print(f"   Found {len(media_files)} media files")
                    for i, media_url in enumerate(media_files):
                        media_response = requests.get(media_url)
                        if media_response.status_code == 200:
                            content_type = media_response.headers.get('content-type', '')
                            if 'video' in content_type:
                                ext = '.mp4'
                            elif 'image' in content_type:
                                ext = '.png'
                            else:
                                ext = '.bin'
                            
                            filename = f"media_{i+1}{ext}"
                            filepath = os.path.join(downloads_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(media_response.content)
                            downloaded_files[f"media_{i+1}"] = filepath
                            print(f"   ✅ Downloaded: {filename}")
                else:
                    print("   🎥 No media files available")
            else:
                print(f"   ⚠️ Media endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading media: {e}")
        
        # 4. Try to download specific output files by common names
        common_output_files = [
            "review_results.json",
            "results.json", 
            "output.json",
            "report.json",
            "data.csv",
            "results.csv",
            "output.txt",
            "log.txt"
        ]
        
        print("📄 Checking for specific output files...")
        for filename in common_output_files:
            try:
                response = self.session.get(f"{self.api_base_url}/task/{task_id}/output-file/{filename}")
                if response.status_code == 200:
                    file_data = response.json()
                    if file_data.get('download_url'):
                        file_response = requests.get(file_data['download_url'])
                        if file_response.status_code == 200:
                            filepath = os.path.join(downloads_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(file_response.content)
                            downloaded_files[filename] = filepath
                            print(f"   ✅ Downloaded: {filename}")
            except Exception as e:
                # Silently continue for missing files
                pass
        
        # 5. Try the generic output file endpoint as fallback
        try:
            print("📋 Checking generic output file...")
            response = self.session.get(f"{self.api_base_url}/get-task-output-file/{task_id}")
            if response.status_code == 200:
                try:
                    # Try to parse as JSON first
                    output_data = response.json()
                    filename = "generic_output.json"
                    filepath = os.path.join(downloads_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                    downloaded_files["generic_output"] = filepath
                    print(f"   ✅ Downloaded: {filename}")
                except json.JSONDecodeError:
                    # Save as text file
                    filename = "generic_output.txt"
                    filepath = os.path.join(downloads_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    downloaded_files["generic_output"] = filepath
                    print(f"   ✅ Downloaded: {filename}")
        except Exception as e:
            print(f"   ❌ Error downloading generic output: {e}")
        
        if downloaded_files:
            print(f"\n✅ Downloaded {len(downloaded_files)} files to {downloads_dir}/")
            for file_type, filepath in downloaded_files.items():
                file_size = os.path.getsize(filepath)
                print(f"   📎 {file_type}: {os.path.basename(filepath)} ({file_size:,} bytes)")
        else:
            print(f"\n📭 No files were available for download")
            
        return downloaded_files

async def main():
    """Main function to run the documentation reviewer."""
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="AI Documentation Reviewer using Browser Use Cloud API")
    parser.add_argument("url", nargs="?", default="https://docs.browser-use.com/introduction", 
                       help="Documentation URL to review")
    parser.add_argument("--max-pages", type=int, default=10, 
                       help="Maximum number of pages to review (default: 10)")
    parser.add_argument("--approach", choices=["one-shot", "multi-step"], default="multi-step",
                       help="Review approach: one-shot or multi-step (default: multi-step)")
    parser.add_argument("--exhaustive", action="store_true",
                       help="Exhaustive mode: discover and review ALL pages on the site (ignores max-pages)")
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.getenv("BROWSER_USE_API_TOKEN"):
        print("❌ Error: Please set your BROWSER_USE_API_TOKEN environment variable")
        print("🔗 Get your API token from: https://browser-use.com")
        print("📝 Add it to your .env file: BROWSER_USE_API_TOKEN=your_token_here")
        return
    
    reviewer = DocumentationReviewer()
    
    print(f"🔍 AI Documentation Reviewer")
    print(f"🌐 Target: {args.url}")
    if args.exhaustive:
        print(f"🕷️  Mode: EXHAUSTIVE (will discover ALL pages)")
        print(f"⚠️  Safety limit: {args.max_pages} pages max")
    else:
        print(f"📊 Max pages: {args.max_pages}")
    print(f"⚙️ Approach: {args.approach}")
    print(f"⏱️  Timeout: Up to 15 minutes per task")
    print(f"🔗 Live sharing: Enabled (URLs will be shown)")
    print("="*60)
    
    try:
        results = await reviewer.review_documentation_site(
            args.url, 
            max_pages=args.max_pages,
            approach=args.approach,
            exhaustive=args.exhaustive
        )
        
        # Check for and display review_results.json file if it exists
        reviewer.check_and_display_results_file()
        
        # Merge results with review_results.json if it exists
        final_results = reviewer.merge_results_with_file(results)
        
        # Save final merged results to file
        mode_suffix = "exhaustive" if args.exhaustive else "limited"
        output_file = f"documentation_review_{args.approach}_{mode_suffix}_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Review completed!")
        print(f"📄 Full report saved to: {output_file}")
        
        # Use final_results for summary display
        results = final_results
        
        # Display downloaded files if any
        if "downloaded_files" in results and results["downloaded_files"]:
            print(f"\n📥 Downloaded {len(results['downloaded_files'])} additional files:")
            for file_type, filepath in results["downloaded_files"].items():
                file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                print(f"   📎 {file_type}: {os.path.basename(filepath)} ({file_size:,} bytes)")
        
        # Print summary
        if "error" not in results:
            # Handle different result structures
            total_reviewed = results.get('total_pages_reviewed', 0)
            total_discovered = results.get('total_pages_discovered', 0)
            
            if total_discovered > 0:
                print(f"🕷️  Pages discovered: {total_discovered}")
            print(f"📊 Pages reviewed: {total_reviewed}")
            
            overall = results.get('overall_review', {}) or results.get('site_analysis', {})
            if 'average_score' in overall:
                print(f"📈 Average score: {overall['average_score']}/10")
                if 'score_distribution' in overall:
                    print(f"🎯 Score distribution: {overall['score_distribution']}")
            
            # Show sample page results
            page_reviews = results.get('page_reviews', [])
            if page_reviews:
                print(f"\n📋 Sample Results:")
                for review in page_reviews[:5]:
                    if isinstance(review, dict):
                        if "scores" in review:
                            score = review["scores"].get("overall", 0)
                            title = review.get("title", "Untitled")[:50]
                            url = review.get("url", "")
                            print(f"  • {score}/10 - {title}")
                            print(f"    {url}")
                        else:
                            # Handle different review structures
                            print(f"  • Review: {str(review)[:100]}...")
                
                if len(page_reviews) > 5:
                    print(f"  ... and {len(page_reviews) - 5} more pages")
            else:
                print(f"📋 No individual page reviews found in result")
                
        else:
            print(f"❌ Review failed: {results['error']}")
            
    except Exception as e:
        print(f"❌ Error during review: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 