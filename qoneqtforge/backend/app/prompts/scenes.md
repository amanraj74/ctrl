Convert the SCRIPT into {n} scenes (average 4-6 seconds each).

For each scene, provide:
- narration: verbatim slice of the script text for this scene
- on_screen_text: <= 6 words, punchy text overlay (or null)
- visual_prompt: concrete image description for a vertical 9:16 composition. Include subject, lighting, camera angle. NO text in image, NO real people/logos.
- visual_source: "ai_image" (default) or "stock"
- stock_query: search query if visual_source is "stock" (else null)
- motion: one of "zoom_in", "zoom_out", "pan_left", "pan_right", "tilt_up" — vary them, never repeat same motion twice in a row
- duration_sec: estimated duration in seconds

Also return ONE style_prefix that keeps all visuals consistent.
Example style_prefix: "cinematic, volumetric light, teal-orange grade, 35mm, ultra detailed"

Scene 1 MUST be the most visually striking (it's the hook).

SCRIPT:
{script}

VISUAL STYLE: {visual_style}

OUTPUT: Return JSON matching this structure:
{
  "style_prefix": "cinematic, volumetric light, ...",
  "scenes": [
    {
      "idx": 0,
      "narration": "...",
      "on_screen_text": "Bold Text Here",
      "visual_prompt": "...",
      "visual_source": "ai_image",
      "stock_query": null,
      "motion": "zoom_in",
      "duration_sec": 5.0
    }
  ]
}

No markdown. Only valid JSON.
