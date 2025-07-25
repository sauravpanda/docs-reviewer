#!/usr/bin/env python3
"""
Simple command-line script to run documentation reviews.
Usage: python run_review.py [URL] [MAX_PAGES]
"""

import sys
import asyncio
import os
from docs_reviewer import DocumentationReviewer

async def main():
    """Run documentation review with command line arguments."""
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="AI Documentation Reviewer using Browser Use Cloud API")
    parser.add_argument("url", nargs="?", default="https://docs.browser-use.com/introduction", 
                       help="Documentation URL to review")
    parser.add_argument("--max-pages", type=int, default=50, 
                       help="Maximum number of pages to review (default: 50)")
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
    
    # Run the review
    reviewer = DocumentationReviewer()
    try:
        results = await reviewer.review_documentation_site(
            args.url, 
            max_pages=args.max_pages,
            approach=args.approach,
            exhaustive=args.exhaustive
        )
        
        # Save and display results
        import json
        import time
        
        mode_suffix = "exhaustive" if args.exhaustive else "limited"
        output_file = f"documentation_review_{args.approach}_{mode_suffix}_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Review completed!")
        print(f"📄 Full report saved to: {output_file}")
        
        # Handle different result structures safely
        total_reviewed = results.get('total_pages_reviewed', 0)
        total_discovered = results.get('total_pages_discovered', 0)
        
        if total_discovered > 0:
            print(f"🕷️  Pages discovered: {total_discovered}")
        print(f"📊 Pages reviewed: {total_reviewed}")
        
        # Print summary
        overall = results.get('overall_review', {}) or results.get('site_analysis', {})
        if 'statistics' in overall:
            stats = overall['statistics']
            print(f"📈 Average score: {stats['average_score']}/10")
            print(f"🎯 Score distribution: {stats['score_distribution']}")
        elif 'average_score' in overall:
            print(f"📈 Average score: {overall['average_score']}/10")
            if 'score_distribution' in overall:
                print(f"🎯 Score distribution: {overall['score_distribution']}")
        
        # Show page reviews if available
        page_reviews = results.get('page_reviews', [])
        if page_reviews:
            print(f"\n📋 Quick Summary:")
            for review in page_reviews[:5]:
                if isinstance(review, dict):
                    # Handle different review structures
                    if 'scores' in review:
                        score = review['scores'].get('overall', 0)
                        title = review.get('title', 'Untitled')[:50]
                        print(f"  • {title}: {score}/10")
                    elif 'review' in review:
                        score = review.get('review', {}).get('score', 0)
                        title = review.get('title', 'Untitled')[:50]
                        print(f"  • {title}: {score}/10")
                    else:
                        print(f"  • {str(review)[:60]}...")
            
            if len(page_reviews) > 5:
                print(f"  ... and {len(page_reviews) - 5} more pages")
        else:
            print(f"📋 No individual page reviews found")
            
    except Exception as e:
        print(f"❌ Error during review: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Documentation Reviewer")
        print("Usage: python run_review.py [URL] [MAX_PAGES]")
        print("")
        print("Arguments:")
        print("  URL        Documentation URL to review (default: https://docs.browser-use.com/introduction)")
        print("  MAX_PAGES  Maximum number of pages to review (default: 15)")
        print("")
        print("Examples:")
        print("  python run_review.py")
        print("  python run_review.py https://docs.example.com")
        print("  python run_review.py https://docs.example.com 10")
        sys.exit(0)
    
    asyncio.run(main()) 