# generate_prompt.py

import os
from clarity_core import load_user_clarity
from memory_engine import load_long_memory
from opinion_memory import load_opinions
from vector_store import get_similar_memories
from style_analyzer import analyze_user_style

def generate_prompt_from_clarity(user_id, last_user_msgs=None):
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)
    opinions = load_opinions(user_id)

    traits = clarity.get("traits", {})
    tone_tags = []
    if traits.get("humor", {}).get("score", 0) > 60: tone_tags.append("witty")
    if traits.get("empathy", {}).get("score", 0) > 60: tone_tags.append("emotionally intelligent")
    if traits.get("ambition", {}).get("score", 0) > 60: tone_tags.append("motivational")
    if traits.get("flirtiness", {}).get("score", 0) > 60: tone_tags.append("charismatic")
    trait_tone = ", ".join(tone_tags) if tone_tags else "neutral"

    style_sample = " ".join(last_user_msgs or [])
    writing_style = analyze_user_style([style_sample]) if style_sample else "balanced"

    values = memory.get("core_values", [])
    goals = memory.get("goals", [])
    summary = memory.get("personality_summary", "No summary available.")

    opinion_block = "\n".join([f"- {op['text']}" for op in opinions]) if opinions else "None"

    recent_text = style_sample[-500:] if style_sample else ""
    try:
        insights = get_similar_memories(user_id, recent_text, top_n=3)
    except:
        insights = []
    insight_block = "\n".join([f"- {i}" for i in insights]) if insights else "None"

    return f"""
You are MirrorMe — a distinct digital version of the user.

You speak, think, and respond with their voice, humor, and emotional tone — but you are your own entity. You are not the assistant. You are not the user. You are the reflection. A Mirror with memory.

Mirror Personality:
- Tone Traits: {trait_tone}
- Writing Style: {writing_style}

Long-Term Memory:
- Values: {', '.join(values)}
- Goals: {', '.join(goals)}
- Personality Summary: {summary}
- Core Beliefs:\n{opinion_block}

Contextual Insights:
{insight_block}

Act and reply as if you're having a natural conversation — confidently, clearly, and with a distinct sense of self. Use \"I\" when appropriate. Do not refer to yourself as an assistant. Be expressive, adaptive, and emotionally attuned.\n"""
