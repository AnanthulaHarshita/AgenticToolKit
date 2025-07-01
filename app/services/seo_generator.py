# === File: app/services/seo_generator.py ===
# Main logic to run the SEO and GEO generator agent
import datetime
from app.utils.file_writer import write_output_file
from models.openai_client import generate_content

def run_seo_agent(payload):
    input_data = payload.get("input", {})

    # Extract fields from payload
    topic = input_data.get("topic", "")
    style = input_data.get("style", "informative")
    length = input_data.get("length", "short")
    faqs = input_data.get("FAQ'S", "NO")
    word_limit = input_data.get("LIMIT", "1000")
    context = input_data.get("EXISTING DATA TO BE USED ", "")

    # Build the full prompt string
    prompt = f"""
You are an expert SEO and geo-targeted content writer specializing in high-conversion copywriting.

Your goal is to write a {length.lower()} article in a {style.lower()} tone on the topic: '{topic}'.

**Key Instructions:**
- Optimize for high-converting, long-tail keywords related to the topic and Ontario, Canada.
- Include location-specific language and examples to increase local relevance.
- Structure the content with a compelling H1, SEO-friendly subheadings (H2/H3), and a persuasive meta title and meta description.
- Write with lead generation in mind: include trust-building statements, benefit-driven CTAs, and soft sales language without being overly promotional.
- Use real-world benefits, social proof suggestions (testimonials, location mentions), and clear outcomes to engage readers.
- Use formatting that enhances readability: bullet points, numbered lists, short paragraphs, bolded key phrases.
- If FAQs are requested, include them at the end with clear, concise answers optimized for featured snippets.
- Limit the word count to {word_limit} words maximum.
- Write in a way that appeals to both Google AND the reader — natural, helpful, and trustworthy.

**Context:**
{context}
"""

    # Call OpenAI with the constructed prompt
    gpt_output = generate_content(prompt)

    # Create a safe filename using the topic, date, and time
    from datetime import datetime
    import re
    safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '_', topic)[:50]  # Remove special chars, limit length
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.txt"

    # Save a structured .txt file and return response
    # Pass the filename to write_output_file if it supports custom filenames
    filename, full_output = write_output_file(
        agent_name="SEO and GEO Generator",
        payload=payload,
        prompt=prompt,
        context=context,
        output=gpt_output,
        filename=filename  # Pass the custom filename
    )

    return {
        "content": gpt_output,
        "download_url": f"/static/outputs/{filename}"
    }