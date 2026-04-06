import os
import re
import yaml
import markdown

# Configuration
MD_POSTS_DIR = '_posts'
OUTPUT_DIR = 'posts'
INDEX_FILE = 'index.html'
TEMPLATE_FILE = 'post_template.html'

def convert_md_to_html(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse Front Matter (Jekyll style)
    parts = re.split(r'---', content)
    if len(parts) >= 3:
        front_matter = yaml.safe_load(parts[1])
        md_content = "---".join(parts[2:])
    else:
        return None

    # Get metadata
    title = front_matter.get('title', 'Untitled Post')
    # Try to extract date from filename if not in front matter (Jekyll style: YYYY-MM-DD-title.md)
    date = front_matter.get('date', '')
    if not date:
        filename = os.path.basename(md_file)
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        date = date_match.group(1) if date_match else "2026-01-01"
    
    # Clean date format to YYYY.MM.DD
    clean_date = date.replace('-', '.') if isinstance(date, str) else date.strftime('%Y.%m.%d')

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])

    # Load template
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # Inject content into template
    final_html = template.replace('{{ title }}', title)
    final_html = final_html.replace('{{ date }}', clean_date)
    final_html = final_html.replace('{{ content }}', html_content)

    # Save to output directory
    output_filename = os.path.basename(md_file).replace('.md', '.html')
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    # Return metadata for index page
    tag = "SYSTEMS"
    if "WiFi" in title or "buildroot" in title.lower(): tag = "HARDENING"
    if "Crash" in title or "Forensics" in title.lower(): tag = "FORENSICS"

    # Create a snippet for the index page
    snippet = re.sub('<[^<]+?>', '', html_content)[:150] + "..."

    return {
        "url": f"posts/{output_filename}",
        "title": title,
        "summary": snippet,
        "date": clean_date,
        "tag": tag
    }

def update_index(posts):
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    html = ""
    for post in posts:
        html += f"""
            <a href="{post['url']}" class="post-entry">
                <h3>{post['title']}</h3>
                <p class="post-summary">{post['summary']}</p>
                <div class="post-meta">
                    <span>DATE // {post['date']}</span>
                    <span class="meta-tag">{post['tag']}</span>
                </div>
            </a>"""
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_content = f.read()

    start_tag = "<!-- POSTS_START -->"
    end_tag = "<!-- POSTS_END -->"
    pattern = re.compile(f"{start_tag}.*?{end_tag}", re.DOTALL)
    new_content = pattern.sub(f"{start_tag}{html}\n            {end_tag}", index_content)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_posts_metadata = []
    
    # Process all Markdown posts
    for filename in os.listdir(MD_POSTS_DIR):
        if filename.endswith('.md'):
            metadata = convert_md_to_html(os.path.join(MD_POSTS_DIR, filename))
            if metadata:
                all_posts_metadata.append(metadata)

    # Update index.html
    update_index(all_posts_metadata)
    print(f"Build Complete: Processed {len(all_posts_metadata)} posts.")

if __name__ == "__main__":
    main()
