#!/usr/bin/env python3
"""
Simple web app to display documentation review JSON files in pretty HTML format.
"""

import os
import json
import glob
from datetime import datetime
from flask import Flask, render_template, request, abort, send_file, url_for
from urllib.parse import quote, unquote
from pathlib import Path

app = Flask(__name__)

def get_json_files():
    """Get all JSON review files in the current directory."""
    patterns = [
        "documentation_review_*.json",
        "review_results.json"
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    file_info = []
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract metadata
            size = os.path.getsize(file)
            modified = datetime.fromtimestamp(os.path.getmtime(file))
            
            # Get review info from JSON
            start_url = data.get('start_url', 'Unknown')
            approach = data.get('review_approach', 'Unknown')
            pages_reviewed = data.get('total_pages_reviewed', 0)
            pages_discovered = data.get('total_pages_discovered', 0)
            avg_score = None
            
            # Try to get average score from different possible locations
            overall_review = data.get('overall_review', {}) or data.get('site_analysis', {})
            if overall_review and 'average_score' in overall_review:
                avg_score = overall_review['average_score']
            
            # Check for downloaded files
            downloaded_files = data.get('downloaded_files', {})
            has_media = bool(downloaded_files and any(os.path.exists(path) for path in downloaded_files.values()))
            
            file_info.append({
                'filename': file,
                'size_kb': round(size / 1024, 1),
                'modified': modified,
                'start_url': start_url,
                'approach': approach,
                'pages_reviewed': pages_reviewed,
                'pages_discovered': pages_discovered,
                'avg_score': avg_score,
                'has_error': 'error' in data,
                'has_ai_generated_file': data.get('has_ai_generated_file', False),
                'downloaded_files': has_media
            })
            
        except Exception as e:
            file_info.append({
                'filename': file,
                'size_kb': round(os.path.getsize(file) / 1024, 1),
                'modified': datetime.fromtimestamp(os.path.getmtime(file)),
                'error': str(e)
            })
    
    return file_info

def organize_downloaded_files(downloaded_files_dict):
    """Organize downloaded files by type for better display."""
    if not downloaded_files_dict:
        return {}
    
    organized = {
        'screenshots': [],
        'recordings': [],
        'media': [],
        'documents': []
    }
    
    for file_type, filepath in downloaded_files_dict.items():
        if not os.path.exists(filepath):
            continue
            
        file_info = {
            'type': file_type,
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'size_kb': round(os.path.getsize(filepath) / 1024, 1),
            'url': url_for('serve_media', filepath=filepath.replace(os.sep, '/'))
        }
        
        # Categorize files
        if 'screenshot' in file_type.lower():
            organized['screenshots'].append(file_info)
        elif 'gif' in file_type.lower() or 'recording' in file_type.lower():
            organized['recordings'].append(file_info)
        elif 'media' in file_type.lower():
            organized['media'].append(file_info)
        elif 'review_results.json' in filepath or filepath.endswith('.json'):
            organized['documents'].append(file_info)
        else:
            organized['documents'].append(file_info)
    
    return organized

def merge_with_review_results(data, downloaded_files):
    """Merge main data with review_results.json if it exists."""
    review_file_path = None
    
    # Look for review_results.json in multiple locations
    if os.path.exists("review_results.json"):
        review_file_path = "review_results.json"
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
            
            print(f"🔗 Merging data from {review_file_path}")
            
            # Create merged data starting with original
            merged_data = data.copy()
            
            # Add AI generated file content
            merged_data["ai_generated_file"] = file_content
            
            if isinstance(file_content, dict):
                # PRIORITY: Use comprehensive page reviews from AI file
                if "page_reviews" in file_content and isinstance(file_content["page_reviews"], list):
                    ai_reviews = file_content["page_reviews"]
                    original_reviews = merged_data.get("page_reviews", [])
                    
                    if len(ai_reviews) > len(original_reviews):
                        # AI file has more comprehensive reviews - use those
                        merged_data["page_reviews"] = ai_reviews
                        print(f"✅ Using {len(ai_reviews)} page reviews from AI file")
                    elif len(ai_reviews) > 0:
                        # Merge both sets
                        if "page_reviews" not in merged_data:
                            merged_data["page_reviews"] = []
                        
                        existing_urls = {page.get("url") for page in merged_data.get("page_reviews", [])}
                        for page_review in ai_reviews:
                            if page_review.get("url") not in existing_urls:
                                merged_data["page_reviews"].append(page_review)
                
                # Update site analysis
                if "site_analysis" in file_content:
                    merged_data["enhanced_site_analysis"] = file_content["site_analysis"]
                    # Also use as overall_review if missing
                    if "overall_review" not in merged_data:
                        merged_data["overall_review"] = file_content["site_analysis"]
                
                # PRIORITY: Use accurate totals from AI file
                if "total_pages_reviewed" in file_content:
                    ai_total = file_content["total_pages_reviewed"]
                    current_total = merged_data.get("total_pages_reviewed", 0)
                    if ai_total > current_total:
                        merged_data["total_pages_reviewed"] = ai_total
                        print(f"✅ Updated total_pages_reviewed: {current_total} → {ai_total}")
                
                if "total_pages_discovered" in file_content:
                    ai_total = file_content["total_pages_discovered"]
                    current_total = merged_data.get("total_pages_discovered", 0)
                    if ai_total > current_total:
                        merged_data["total_pages_discovered"] = ai_total
                        print(f"✅ Updated total_pages_discovered: {current_total} → {ai_total}")
            
            merged_data["has_ai_generated_file"] = True
            
            # Calculate summary statistics for template
            if "page_reviews" in merged_data and merged_data["page_reviews"]:
                reviews = merged_data["page_reviews"]
                scores = []
                excellent_count = 0
                
                for page in reviews:
                    if isinstance(page, dict) and "scores" in page and "overall" in page["scores"]:
                        score = page["scores"]["overall"]
                        if isinstance(score, (int, float)):
                            scores.append(score)
                            if score >= 8:
                                excellent_count += 1
                
                if scores:
                    merged_data["summary_stats"] = {
                        "average_score": sum(scores) / len(scores),
                        "excellent_count": excellent_count,
                        "total_with_scores": len(scores)
                    }
                else:
                    merged_data["summary_stats"] = {
                        "average_score": 0,
                        "excellent_count": 0,
                        "total_with_scores": 0
                    }
            else:
                merged_data["summary_stats"] = {
                    "average_score": 0,
                    "excellent_count": 0,
                    "total_with_scores": 0
                }
            
            print(f"✅ Successfully merged review data")
            return merged_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Could not parse {review_file_path}: {e}")
            data["ai_file_error"] = f"JSON parsing error: {str(e)}"
            return data
        except Exception as e:
            print(f"⚠️ Error reading {review_file_path}: {e}")
            data["ai_file_error"] = f"File reading error: {str(e)}"
            return data
    else:
        print("📄 No review_results.json found")
        data["has_ai_generated_file"] = False
        return data

@app.route('/media/<path:filepath>')
def serve_media(filepath):
    """Serve downloaded media files."""
    try:
        # Security check - ensure file exists and is in a safe location
        if '..' in filepath or filepath.startswith('/'):
            abort(404)
        
        full_path = os.path.abspath(filepath)
        if not os.path.exists(full_path):
            abort(404)
            
        return send_file(full_path)
    except Exception:
        abort(404)

@app.route('/')
def index():
    """Display list of available JSON files."""
    files = get_json_files()
    return render_template('index.html', files=files)

@app.route('/view/<path:filename>')
def view_file(filename):
    """Display a specific JSON file in pretty HTML format."""
    # Security check - only allow files in current directory
    if '/' in filename or '\\' in filename or '..' in filename:
        abort(404)
    
    if not os.path.exists(filename):
        abort(404)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Organize downloaded files for display
        downloaded_files = data.get('downloaded_files', {})
        
        # Auto-detect review_results.json if it exists in task folders
        if downloaded_files:
            # Find the task folder from any downloaded file
            sample_path = next(iter(downloaded_files.values()), "")
            if sample_path and "/" in sample_path:
                task_folder = "/".join(sample_path.split("/")[:-1])
                review_results_path = f"{task_folder}/review_results.json"
                if os.path.exists(review_results_path):
                    # Add it to downloaded files if not already there
                    has_review_file = any("review_results.json" in path for path in downloaded_files.values())
                    if not has_review_file:
                        downloaded_files["review_results"] = review_results_path
        
        # Merge data with review_results.json if it exists
        merged_data = merge_with_review_results(data, downloaded_files)
        
        organized_files = organize_downloaded_files(downloaded_files)
        
        return render_template('view.html', 
                             filename=filename, 
                             data=merged_data, 
                             media_files=organized_files)
        
    except json.JSONDecodeError as e:
        return render_template('error.html', 
                             filename=filename, 
                             error=f"Invalid JSON: {str(e)}")
    except Exception as e:
        return render_template('error.html', 
                             filename=filename, 
                             error=f"Error reading file: {str(e)}")

@app.route('/raw/<path:filename>')
def raw_file(filename):
    """Display raw JSON content."""
    # Security check
    if '/' in filename or '\\' in filename or '..' in filename:
        abort(404)
    
    if not os.path.exists(filename):
        abort(404)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f'<pre style="font-family: monospace; white-space: pre-wrap; padding: 20px;">{content}</pre>'
        
    except Exception as e:
        return f'<p>Error reading file: {str(e)}</p>'

@app.route('/debug/<path:filename>')
def debug_file(filename):
    """Debug route to show merged data structure."""
    # Security check
    if '/' in filename or '\\' in filename or '..' in filename:
        abort(404)
    
    if not os.path.exists(filename):
        abort(404)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        downloaded_files = data.get('downloaded_files', {})
        
        # Auto-detect review_results.json
        if downloaded_files:
            sample_path = next(iter(downloaded_files.values()), "")
            if sample_path and "/" in sample_path:
                task_folder = "/".join(sample_path.split("/")[:-1])
                review_results_path = f"{task_folder}/review_results.json"
                if os.path.exists(review_results_path):
                    has_review_file = any("review_results.json" in path for path in downloaded_files.values())
                    if not has_review_file:
                        downloaded_files["review_results"] = review_results_path
        
        merged_data = merge_with_review_results(data, downloaded_files)
        
        debug_info = {
            "original_page_count": data.get('total_pages_reviewed', 0),
            "merged_page_count": merged_data.get('total_pages_reviewed', 0),
            "has_page_reviews": len(merged_data.get('page_reviews', [])),
            "has_ai_file": merged_data.get('has_ai_generated_file', False),
            "downloaded_files_count": len(downloaded_files),
            "review_results_path": None
        }
        
        # Find review_results path
        for file_type, filepath in downloaded_files.items():
            if "review_results.json" in filepath:
                debug_info["review_results_path"] = filepath
                break
        
        return f'<pre style="font-family: monospace; white-space: pre-wrap; padding: 20px;">{json.dumps(debug_info, indent=2)}</pre>'
        
    except Exception as e:
        return f'<p>Error: {str(e)}</p>'

if __name__ == '__main__':
    print("🌐 Starting Documentation Review Viewer")
    print("📂 Scanning for JSON files...")
    
    files = get_json_files()
    print(f"📄 Found {len(files)} review files")
    
    print("\n🚀 Starting web server...")
    print("🔗 Open your browser to: http://localhost:5002")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5002) 