# Importing necessary modules
import wikipedia
from flask import Flask, render_template, request, make_response
import requests
from bs4 import BeautifulSoup
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
import io
import re
from datetime import datetime
import spacy # Added for entity highlighting
from groq import Groq # Changed to Groq

# --- AI and NLP Configuration ---
# 1. Configure the Groq API
# IMPORTANT: Your API key is already included
try:
    client = Groq(api_key="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")
    print("Groq AI Model configured successfully.")
    
    # Test the model to ensure it's working
    test_response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        model="llama3-8b-8192",
        max_tokens=10,
        temperature=0.3
    )
    print("Model test successful!")
    
except Exception as e:
    client = None
    print(f"Error configuring Groq AI Model: {e}. AI features will be disabled.")

# 2. Load the SpaCy model for entity highlighting
try:
    nlp = spacy.load("en_core_web_sm")
    print("SpaCy model loaded successfully.")
except Exception as e:
    nlp = None
    print(f"Error loading SpaCy model: {e}. Entity highlighting will be disabled.")


# Creating an instance of the Flask class
app = Flask(__name__)

# Registering the 'zip' function as a Jinja2 filter
app.jinja_env.filters["zip"] = zip

# Setting the cache-control header to disable caching of static files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# --- AI & NLP Functions ---

def get_ai_response_with_groq(text, question):
    """Generate AI response using Groq API."""
    if not client:
        return {
            'answer': "AI Model not configured. Please check your API key.",
            'summary_points': ["AI Model not available"]
        }
    
    # Create a comprehensive prompt for both answer and summary
    prompt = f"""Based on the following information about '{question}', please provide:

1. A direct, comprehensive answer to the question
2. Exactly 5 key summary points about the topic

Information: {text[:3000]}

Question: {question}

Please format your response as follows:
ANSWER: [Your detailed answer here]

SUMMARY POINTS:
1. [First key point]
2. [Second key point]
3. [Third key point]
4. [Fourth key point]
5. [Fifth key point]

Make sure each summary point is informative and captures important aspects of the topic."""
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=800,
            temperature=0.3
        )
        
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content.strip()
            
            # Parse the response to extract answer and summary points
            answer = ""
            summary_points = []
            
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('ANSWER:'):
                    current_section = 'answer'
                    answer = line.replace('ANSWER:', '').strip()
                elif line.startswith('SUMMARY POINTS:'):
                    current_section = 'summary'
                elif current_section == 'answer' and line and not line.startswith('SUMMARY'):
                    if answer:
                        answer += " " + line
                    else:
                        answer = line
                elif current_section == 'summary' and line and (line[0].isdigit() or line.startswith('-')):
                    # Clean up the point
                    cleaned_point = re.sub(r'^[\d\.\-\*\•]\s*', '', line)
                    if cleaned_point and len(cleaned_point) > 10:
                        summary_points.append(cleaned_point)
            
            # Ensure we have exactly 5 points
            while len(summary_points) < 5:
                summary_points.append(f"{question} is an important topic that requires further exploration.")
            
            return {
                'answer': answer if answer else f"Based on the available information, {question} is a significant topic with various aspects to explore.",
                'summary_points': summary_points[:5]
            }
        else:
            return {
                'answer': f"Could not generate AI response for {question}. Please try again.",
                'summary_points': [f"Unable to generate summary for {question}"]
            }
            
    except Exception as e:
        print(f"Error with Groq API: {e}")
        return {
            'answer': f"AI response generation encountered an error: {str(e)}",
            'summary_points': [
                f"AI summary generation encountered an error.",
                f"Please check your internet connection and API key.",
                f"You can still use the Wikipedia search results below.",
                f"The search results contain comprehensive information about {question}.",
                f"Consider trying the AI response again or contact support if the issue persists."
            ]
        }

def highlight_entities(text):
    """Highlight named entities in text using SpaCy."""
    if not nlp:
        return text # Return original text if SpaCy isn't loaded
    
    try:
        doc = nlp(text)
        # Define colors for different entity types
        entity_colors = {
            "PERSON": "#ffadad", # Red
            "GPE": "#a0c4ff",     # Blue (Geopolitical Entity)
            "ORG": "#fdffb6",     # Yellow (Organization)
            "DATE": "#caffbf",    # Green
            "MONEY": "#caffbf",
            "PRODUCT": "#ffd6a5", # Orange
            "EVENT": "#ffc6ff",   # Pink
            "LOC": "#a0c4ff"      # Blue (Location)
        }
        
        highlighted_text = text
        # Iterate backwards to not mess up indices
        for ent in reversed(doc.ents):
            label = ent.label_
            color = entity_colors.get(label, "#e0e0e0") # Default grey
            highlight = f'<mark class="entity" style="background-color:{color}; padding: 2px 4px; border-radius: 4px; line-height: 1.8;">{ent.text} <span class="entity-label">{label}</span></mark>'
            start, end = ent.start_char, ent.end_char
            highlighted_text = highlighted_text[:start] + highlight + highlighted_text[end:]
            
        return highlighted_text
    except Exception as e:
        print(f"Error in entity highlighting: {e}")
        return text

def get_additional_references(keyword):
    """Get additional reference links from various sources"""
    references = []
    try:
        references.append({'title': f"Academic Research on {keyword}",'url': f"https://scholar.google.com/scholar?q={keyword.replace(' ', '+')}",'source': "Google Scholar",'type': "Academic"})
        references.append({'title': f"{keyword} - Encyclopedia Britannica",'url': f"https://www.britannica.com/search?query={keyword.replace(' ', '+')}",'source': "Britannica",'type': "Encyclopedia"})
        references.append({'title': f"Learn about {keyword} - Khan Academy",'url': f"https://www.khanacademy.org/search?search_again=1&page_search_query={keyword.replace(' ', '+')}",'source': "Khan Academy",'type': "Educational"})
        references.append({'title': f"Online Courses on {keyword}",'url': f"https://www.coursera.org/search?query={keyword.replace(' ', '+')}",'source': "Coursera",'type': "Course"})
        references.append({'title': f"Research Papers on {keyword}",'url': f"https://www.researchgate.net/search?q={keyword.replace(' ', '+')}",'source': "ResearchGate",'type': "Research"})
        references.append({'title': f"Educational Videos on {keyword}",'url': f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}+education",'source': "YouTube",'type': "Video"})
    except Exception as e:
        print(f"Error getting additional references: {e}")
    return references

def create_pdf(keyword, ai_answer, ai_summary_points, wikipedia_results, additional_refs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle('CustomTitle',parent=styles['Heading1'],fontSize=20,spaceAfter=30,textColor='darkblue',alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading',parent=styles['Heading2'],fontSize=14,spaceAfter=12,textColor='darkred')
    
    story.append(Paragraph(f"AI Research Summary: {keyword}", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Add AI Answer
    story.append(Paragraph("AI Answer", heading_style))
    story.append(Paragraph(ai_answer, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # AI Summary Points
    story.append(Paragraph("AI-Powered Key Points Summary", heading_style))
    for i, point in enumerate(ai_summary_points, 1):
        story.append(Paragraph(f"{i}. {point}", styles['Normal']))
        story.append(Spacer(1, 6))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Wikipedia Sources", heading_style))
    for i, (title, link, info) in enumerate(wikipedia_results, 1):
        story.append(Paragraph(f"<b>{i}. {title}</b>", styles['Normal']))
        story.append(Paragraph(info, styles['Normal']))
        story.append(Paragraph(f"<link href='{link}'>Read more: {link}</link>", styles['Normal']))
        story.append(Spacer(1, 12))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Additional References", heading_style))
    for ref in additional_refs:
        story.append(Paragraph(f"<b>{ref['title']}</b> ({ref['type']})", styles['Normal']))
        story.append(Paragraph(f"Source: {ref['source']}", styles['Normal']))
        story.append(Paragraph(f"<link href='{ref['url']}'>{ref['url']}</link>", styles['Normal']))
        story.append(Spacer(1, 10))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated by SenimSearcherX Bot - Powered by Groq AI & Senim Solution LLP", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
    doc.build(story)
    buffer.seek(0)
    return buffer

def finder_x(keyword):
    initial_results = wikipedia.search(keyword, results=15)
    tp, linksforpage, pageinfoforhtml = [], [], []
    successful_results, max_results = 0, 8
    
    for x in initial_results:
        if successful_results >= max_results: break
        try:
            page = wikipedia.page(x, auto_suggest=False, redirect=False)
            tp.append(x)
            linksforpage.append(page.url)
            page_summary = wikipedia.summary(x, sentences=2, auto_suggest=False, redirect=False)
            pageinfoforhtml.append(page_summary)
            successful_results += 1
        except Exception: continue
    
    # Get full content for AI processing
    try:
        full_content_for_ai = wikipedia.page(tp[0], auto_suggest=False).content
    except:
        full_content_for_ai = " ".join(pageinfoforhtml)
        
    return tp, linksforpage, pageinfoforhtml, full_content_for_ai

# --- Main App Route (Updated) ---
@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method != "POST":
        return render_template("index.html")
    
    userinput = request.form.get("pswd")
    
    if not userinput or userinput.strip() == "":
        return render_template("index.html")
    
    userinput_clean = userinput.strip().title()
    heading, links, info, full_content = finder_x(userinput_clean)
    
    # Generate AI response with both answer and summary
    combined_text = " ".join(info[:3]) if info else ""
    ai_response = get_ai_response_with_groq(combined_text + " " + full_content[:2000], userinput_clean)
    
    # Highlight entities in Wikipedia summaries
    highlighted_info = [highlight_entities(text) for text in info]
    
    return render_template(
        "index.html",
        si=userinput_clean,
        sz=list(zip(heading, links, highlighted_info)),
        ai_answer=ai_response['answer'],
        ai_summary_points=ai_response['summary_points'],
        additional_refs=get_additional_references(userinput_clean)
    )

@app.route("/download_pdf")
def download_pdf():
    keyword = request.args.get('keyword', 'Search Results')
    heading, links, info, full_content = finder_x(keyword)
    
    # Generate AI response
    combined_text = " ".join(info[:3]) if info else ""
    ai_response = get_ai_response_with_groq(combined_text + " " + full_content[:2000], keyword)
    
    additional_refs = get_additional_references(keyword)
    pdf_buffer = create_pdf(keyword, ai_response['answer'], ai_response['summary_points'], list(zip(heading, links, info)), additional_refs)
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={keyword.replace(" ", "_")}_ai_research_summary.pdf'
    return response

if __name__ == "__main__":
    app.run(debug=True)