"""Gradio interface for hadith search with Islamic-themed professional UI."""

import gradio as gr

from src.search.hybrid_search import hybrid_search


# Islamic-themed professional CSS - Light cream/beige background
CUSTOM_CSS = """
/* Islamic color palette - Cream, Gold, Deep Green accents */
.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
    background: linear-gradient(180deg, #faf8f5 0%, #f5f2ed 50%, #ebe6df 100%) !important;
    min-height: 100vh;
}

/* Custom scrollbar with gold accent */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #f5f2ed;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #c9a227, #8b7355);
    border-radius: 4px;
}

/* Islamic geometric pattern overlay (subtle) */
.gradio-container::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        radial-gradient(circle at 25% 25%, rgba(201, 162, 39, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 75% 75%, rgba(16, 110, 77, 0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* Search input styling - Dark background for visibility */
.search-input input {
    background: #1a2f25 !important;
    border: 2px solid rgba(16, 110, 77, 0.4) !important;
    border-radius: 12px !important;
    color: #f0f0f0 !important;
    font-size: 16px !important;
    padding: 16px 20px !important;
    transition: all 0.3s ease !important;
}

.search-input input:focus {
    border-color: #059669 !important;
    box-shadow: 0 0 20px rgba(16, 110, 77, 0.25) !important;
}

.search-input input::placeholder {
    color: rgba(255, 255, 255, 0.6) !important;
}

/* Primary button - Emerald with gold hover */
button.primary {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 32px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(16, 110, 77, 0.25) !important;
}

button.primary:hover {
    background: linear-gradient(135deg, #c9a227 0%, #d4af37 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(201, 162, 39, 0.35) !important;
}

/* Markdown prose styling for light background */
.prose {
    color: #2d3748 !important;
}

.prose h2 {
    color: #8b6914 !important;
    font-weight: 700 !important;
}

.prose h3 {
    color: #047857 !important;
    font-weight: 600 !important;
}

.prose strong {
    color: #1a202c !important;
}

.prose em {
    color: #065f46 !important;
}

.prose blockquote {
    background: rgba(16, 110, 77, 0.08) !important;
    border-left: 4px solid #059669 !important;
    border-radius: 0 12px 12px 0 !important;
    padding: 16px 20px !important;
    margin: 16px 0 !important;
    font-style: normal !important;
    color: #1a202c !important;
}

.prose hr {
    border-color: rgba(201, 162, 39, 0.25) !important;
    margin: 24px 0 !important;
}

/* Table styling */
.prose table {
    border-collapse: collapse;
    width: 100%;
}

.prose th {
    background: rgba(16, 110, 77, 0.12) !important;
    color: #047857 !important;
    padding: 12px !important;
    border: 1px solid rgba(16, 110, 77, 0.2) !important;
}

.prose td {
    padding: 10px 12px !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    color: #2d3748 !important;
}

/* Label styling */
label {
    color: #047857 !important;
    font-weight: 500 !important;
}

/* Block backgrounds */
.block {
    background: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
}

/* Examples section - dark text on light background */
.examples-row button,
.gallery button,
button.secondary {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(16, 110, 77, 0.2) !important;
    color: #1a202c !important;
}

.examples-row button:hover,
.gallery button:hover,
button.secondary:hover {
    background: rgba(16, 110, 77, 0.1) !important;
    border-color: rgba(16, 110, 77, 0.4) !important;
}

/* Example text styling */
.examples-row span,
.gallery span {
    color: #2d3748 !important;
}
"""


def format_results(results: list, query: str, expanded_query: str, cached: bool, took_ms: float) -> str:
    """Format search results with Islamic styling."""
    if not results:
        return """
## 🔍 No Results Found

<div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 20px; margin: 16px 0;">

**Try different phrasing:**
- Use English descriptions: *"raising hands during prayer"* instead of transliterated Arabic
- Be specific: *"rights of neighbors"* or *"treating parents kindly"*
- Try related topics: *"prayer positions"* or *"fasting rules"*

</div>
"""

    # Header with stats
    cache_icon = "⚡" if cached else "🔍"
    cache_text = "Cached" if cached else "Fresh Search"
    
    output = [
        f"## ✨ Found {len(results)} Hadiths",
        "",
        f"<div style='display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px;'>",
        f"<span style='background: rgba(16, 110, 77, 0.12); border: 1px solid rgba(16, 110, 77, 0.25); padding: 6px 14px; border-radius: 20px; font-size: 13px; color: #047857;'>{cache_icon} {cache_text} • {took_ms:.0f}ms</span>",
        f"</div>",
        "",
    ]

    for i, r in enumerate(results, 1):
        # Book styling with Islamic colors
        if r['book'] == 'bukhari':
            book_color = "rgba(16, 110, 77, 0.1)"
            book_border = "rgba(16, 110, 77, 0.3)"
            book_icon = "📗"
            book_name = "Sahih al-Bukhari"
        else:
            book_color = "rgba(59, 130, 246, 0.1)"
            book_border = "rgba(59, 130, 246, 0.3)"
            book_icon = "📘"
            book_name = "Sahih Muslim"
        
        # Score color
        score_pct = r['score'] * 100
        if score_pct >= 70:
            score_color = "#059669"
        elif score_pct >= 30:
            score_color = "#b8860b"
        else:
            score_color = "#6b7280"
        
        output.append(f"### {book_icon} Hadith {i}")
        output.append(f"<div style='background: {book_color}; border: 1px solid {book_border}; border-radius: 10px; padding: 6px 14px; display: inline-block; margin-bottom: 10px;'>")
        output.append(f"<strong style='color: #1a202c;'>{book_name}</strong> — <span style='color: #047857;'>Volume {r['volume']}, Hadith #{r['hadith_number']}</span>")
        output.append(f"</div>")
        output.append("")
        
        if r['chapter'] and r['chapter'] != 'Unknown':
            chapter_clean = r['chapter'][:80] + "..." if len(r['chapter']) > 80 else r['chapter']
            output.append(f"📖 *Chapter: {chapter_clean}*")
        
        if r['narrator'] and len(r['narrator']) > 3:
            narrator_clean = r['narrator'][:80] + "..." if len(r['narrator']) > 80 else r['narrator']
            output.append(f"*Narrated by: {narrator_clean}*")
        
        output.append("")
        
        # Hadith text in blockquote - show full text
        output.append(f"> {r['text']}")
        
        output.append("")
        output.append(f"<span style='color: {score_color}; font-size: 13px;'>📊 Relevance: **{score_pct:.1f}%**</span>")
        output.append("")
        output.append("---")
        output.append("")

    return "\n".join(output)


def search_fn(query: str) -> str:
    """Search function for Gradio interface."""
    # Check if indexing is in progress
    try:
        from startup import get_indexing_status
        status = get_indexing_status()
        if status["in_progress"]:
            return """
## ⏳ Database Initialization in Progress

<div style="background: rgba(201, 162, 39, 0.15); border: 1px solid rgba(201, 162, 39, 0.4); border-radius: 12px; padding: 24px; margin: 16px 0;">

**The hadith database is currently being indexed.** This is a one-time process that takes approximately 20-30 minutes.

🔄 **Please check back in a few minutes** — the search will be fully functional once indexing completes.

Thank you for your patience!

</div>
"""
        elif status["error"]:
            return f"""
## ⚠️ Database Error

<div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 20px;">

An error occurred during database initialization: `{status['error']}`

Please contact support or try again later.

</div>
"""
    except ImportError:
        pass  # startup module not available (running standalone)
    
    if not query.strip():
        return """
<div style="text-align: center; padding: 40px 20px;">

### Welcome to the Hadith Search Engine

Enter a question or topic above to search authentic hadiths from **Sahih al-Bukhari** and **Sahih Muslim**.

</div>

---

<div style="background: rgba(16, 110, 77, 0.08); border: 1px solid rgba(16, 110, 77, 0.2); border-radius: 16px; padding: 24px; margin: 20px 0;">

### 💡 Search Tips

| Tip | Example |
|-----|---------|
| Use English descriptions | *"raising hands during prayer"* |
| Be specific with topics | *"rights of neighbors in Islam"* |
| Ask naturally | *"How did the Prophet ﷺ pray?"* |

</div>

<div style="background: rgba(201, 162, 39, 0.1); border: 1px solid rgba(201, 162, 39, 0.25); border-radius: 16px; padding: 24px; margin: 20px 0;">

### ⭐ Why Use This Tool?

- **Authentic Sources Only** — Direct from verified hadith collections
- **No AI Hallucination** — Returns exact hadith text, never fabricates
- **Proper Citations** — Book, Volume, and Hadith numbers included

</div>
"""

    try:
        results, expanded_query, cached, took_ms = hybrid_search(query, top_k=10)
        return format_results(results, query, expanded_query, cached, took_ms)

    except Exception as e:
        return f"""
## ⚠️ Error Occurred

<div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 20px;">

Something went wrong: `{str(e)}`

Please try again or refine your search query.

</div>
"""


def create_gradio_app() -> gr.Blocks:
    """Create Islamic-themed professional Gradio interface."""
    theme = gr.themes.Base(
        primary_hue="emerald",
        secondary_hue="amber",
        neutral_hue="stone",
        font=("Inter", "system-ui", "-apple-system", "sans-serif"),
    ).set(
        body_background_fill="#faf8f5",
        body_background_fill_dark="#faf8f5",
        block_background_fill="rgba(255, 255, 255, 0.7)",
        block_background_fill_dark="rgba(255, 255, 255, 0.7)",
        block_border_color="rgba(0, 0, 0, 0.08)",
        block_border_color_dark="rgba(0, 0, 0, 0.08)",
        block_label_text_color="#047857",
        block_label_text_color_dark="#047857",
        block_title_text_color="#1a202c",
        block_title_text_color_dark="#1a202c",
        body_text_color="#2d3748",
        body_text_color_dark="#2d3748",
        body_text_color_subdued="#6b7280",
        body_text_color_subdued_dark="#6b7280",
        button_primary_background_fill="linear-gradient(135deg, #059669 0%, #10b981 100%)",
        button_primary_background_fill_dark="linear-gradient(135deg, #059669 0%, #10b981 100%)",
        button_primary_background_fill_hover="linear-gradient(135deg, #c9a227 0%, #d4af37 100%)",
        button_primary_background_fill_hover_dark="linear-gradient(135deg, #c9a227 0%, #d4af37 100%)",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        input_background_fill="#1a2f25",
        input_background_fill_dark="#1a2f25",
        input_border_color="rgba(16, 110, 77, 0.4)",
        input_border_color_dark="rgba(16, 110, 77, 0.4)",
        input_border_color_focus="rgba(5, 150, 105, 0.7)",
        input_border_color_focus_dark="rgba(5, 150, 105, 0.7)",
        shadow_drop="0 4px 20px rgba(0, 0, 0, 0.08)",
        shadow_drop_lg="0 8px 32px rgba(0, 0, 0, 0.12)",
    )
    
    with gr.Blocks(theme=theme, css=CUSTOM_CSS, title="Hadith Search | Islamic Hadith Database") as app:
        
        # Islamic Header with Bismillah (only once)
        gr.HTML("""
        <div style="text-align: center; padding: 40px 20px 30px; background: linear-gradient(180deg, rgba(16, 110, 77, 0.08) 0%, transparent 100%); border-bottom: 1px solid rgba(201, 162, 39, 0.2); margin-bottom: 32px;">
            
            <!-- Bismillah -->
            <p style="font-size: 1.8em; color: #8b6914; margin: 0 0 20px 0; font-family: 'Traditional Arabic', 'Scheherazade', serif; direction: rtl;">
                بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
            </p>
            
            <!-- Decorative line -->
            <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 20px;">
                <div style="height: 1px; width: 60px; background: linear-gradient(90deg, transparent, #c9a227);"></div>
                <span style="color: #c9a227; font-size: 1.2em;">✦</span>
                <div style="height: 1px; width: 60px; background: linear-gradient(90deg, #c9a227, transparent);"></div>
            </div>
            
            <!-- Title -->
            <h1 style="font-size: 2.4em; font-weight: 700; color: #1a202c; margin: 0 0 10px 0; letter-spacing: -0.5px;">
                📚 Hadith Search Engine
            </h1>
            <p style="font-size: 1.1em; color: #047857; margin: 0 0 6px 0; font-weight: 500;">
                Sahih al-Bukhari & Sahih Muslim
            </p>
            <p style="font-size: 0.9em; color: #6b7280; margin: 0;">
                Semantic search powered by AI • Authentic sources only
            </p>
        </div>
        """)
        
        # Search Section
        with gr.Row():
            with gr.Column(scale=5):
                query_input = gr.Textbox(
                    label="🔍 Search the Hadith",
                    placeholder="Enter your question... e.g., 'What did the Prophet ﷺ say about kindness to parents?'",
                    lines=1,
                    max_lines=1,
                    elem_classes=["search-input"]
                )
            with gr.Column(scale=1, min_width=140):
                search_btn = gr.Button("Search", variant="primary", size="lg")
        
        # Results Area (no repeated Bismillah)
        results_output = gr.Markdown(
            value="""
<div style="text-align: center; padding: 40px 20px;">

### Welcome to the Hadith Search Engine

Enter a question or topic above to search authentic hadiths from **Sahih al-Bukhari** and **Sahih Muslim**.

</div>

---

<div style="background: rgba(16, 110, 77, 0.08); border: 1px solid rgba(16, 110, 77, 0.2); border-radius: 16px; padding: 24px; margin: 20px 0;">

### 💡 Search Tips

| Tip | Example |
|-----|---------|
| Use English descriptions | *"raising hands during prayer"* |
| Be specific with topics | *"rights of neighbors in Islam"* |
| Ask naturally | *"How did the Prophet ﷺ pray?"* |

</div>

<div style="background: rgba(201, 162, 39, 0.1); border: 1px solid rgba(201, 162, 39, 0.25); border-radius: 16px; padding: 24px; margin: 20px 0;">

### ⭐ Why Use This Tool?

- **Authentic Sources Only** — Direct from verified hadith collections
- **No AI Hallucination** — Returns exact hadith text, never fabricates
- **Proper Citations** — Book, Volume, and Hadith numbers included

</div>
            """
        )
        
        # Example Queries Section
        gr.HTML("""
        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(201, 162, 39, 0.2);">
            <h3 style="color: #8b6914; font-weight: 600; margin-bottom: 12px; font-size: 1em;">
                ✦ Example Queries
            </h3>
        </div>
        """)
        
        examples = gr.Examples(
            examples=[
                ["How to perform prayer correctly"],
                ["Raising hands during prayer (Rafa Yadain)"],
                ["Rights and treatment of parents in Islam"],
                ["What are the rights of neighbors"],
                ["What breaks the fast in Ramadan"],
                ["Patience during hardship and trials"],
                ["Virtues of honesty and truthfulness"],
                ["Kindness to animals in Islam"],
            ],
            inputs=query_input
        )
        
        # Footer with Islamic decorative elements
        gr.HTML("""
        <div style="margin-top: 48px; padding: 30px 20px; text-align: center; border-top: 1px solid rgba(201, 162, 39, 0.2); background: linear-gradient(0deg, rgba(16, 110, 77, 0.05) 0%, transparent 100%);">
            
            <!-- Decorative element -->
            <div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 20px;">
                <div style="height: 1px; width: 40px; background: linear-gradient(90deg, transparent, rgba(201, 162, 39, 0.5));"></div>
                <span style="color: #c9a227; font-size: 0.9em;">☪</span>
                <div style="height: 1px; width: 40px; background: linear-gradient(90deg, rgba(201, 162, 39, 0.5), transparent);"></div>
            </div>
            
            <!-- Stats -->
            <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; margin-bottom: 20px;">
                <span style="background: rgba(16, 110, 77, 0.08); border: 1px solid rgba(16, 110, 77, 0.2); padding: 8px 18px; border-radius: 24px; color: #047857; font-size: 13px;">
                    📊 12,738 Hadiths
                </span>
                <span style="background: rgba(16, 110, 77, 0.08); border: 1px solid rgba(16, 110, 77, 0.2); padding: 8px 18px; border-radius: 24px; color: #047857; font-size: 13px;">
                    📗 Sahih Bukhari: 7,387
                </span>
                <span style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.2); padding: 8px 18px; border-radius: 24px; color: #2563eb; font-size: 13px;">
                    📘 Sahih Muslim: 5,351
                </span>
            </div>
            
            <p style="color: #6b7280; font-size: 13px; margin-bottom: 16px;">
                <em>📜 Authentic hadith text with verified references — No AI hallucination</em>
            </p>
            

        </div>
        """)

        # Connect events
        search_btn.click(fn=search_fn, inputs=query_input, outputs=results_output)
        query_input.submit(fn=search_fn, inputs=query_input, outputs=results_output)

    return app
