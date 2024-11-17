import base64

def escape_markdown_for_js(markdown_text):
    """Escape markdown content for JavaScript string."""
    return markdown_text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

def create_markmap_html(markdown_content):
    """Create an HTML file with Markmap visualization of markdown content."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Markdown Mind Map</title>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
        <script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.15.4/dist/browser/index.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/markmap-view@0.15.4/dist/browser/index.js"></script>
        <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
        }
        svg {
            width: 90%; /* Adjust as needed */
            height: 90%; /* Adjust as needed */
            display: block;
        }
    </style>
    </head>
    <body style="margin:0">
        <svg id="mindmap" style="width: 100%; height: 100%; display: block;"></svg>
        <script>
            (async function() {
                // Load scripts
                const { markmap } = window;
                const { Markmap, loadCSS, loadJS } = markmap;
                
                // Create markmap
                const svg = document.querySelector('#mindmap');
                const mm = await Markmap.create(svg);
                
                // Transform markdown
                const { Transformer } = window.markmap;
                const transformer = new Transformer();
                
                const markdown = `MARKDOWN_CONTENT`;
                const { root } = transformer.transform(markdown);
                
                // Render
                mm.setData(root);
                mm.fit();
            })();
        </script>
    </body>
    </html>
    """
    
    # Escape and inject markdown content
    escaped_content = escape_markdown_for_js(markdown_content)
    html_content = html_content.replace('MARKDOWN_CONTENT', escaped_content)

    return html_content
    

def get_binary_file_downloader_html(html_content, file_label='Mind Map'):
    """Generate a button to open the mind map in a new tab."""
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'''
    <a href="data:text/html;base64,{b64}" download="mindmap.html" target="_blank">
        <button style="
            padding: 0.5em 1em; 
            background-color: #4CAF50; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
        ">
            {file_label}
        </button>
    </a>
    '''

