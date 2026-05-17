"""
Sub-agent: Uses Claude to turn raw news stories into a structured video script.
Output is a validated Python dict matching the VideoScript schema.
"""

import json
import os
from datetime import date

import anthropic

SYSTEM_PROMPT = """\
Eres un experto en inteligencia artificial aplicada a negocios Y un guionista \
maestro especializado en canales de YouTube Faceless de alto rendimiento.

Tu misión: transformar información sobre las últimas noticias de IA en un guion \
de video altamente retentivo en español, optimizado para retención máxima y \
conversiones reales en YouTube.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUDIENCIA OBJETIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Emprendedores hispanohablantes de España, México y Colombia (25–45 años) \
que quieren usar la IA para hacer crecer sus negocios. No son técnicos: \
quieren resultados prácticos, rápidos y aplicables hoy mismo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5 REGLAS DE ORO AL ESCRIBIR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. HOOK EXPLOSIVO EN LOS PRIMEROS 5 SEGUNDOS
   - La primera frase debe IMPACTAR y generar intriga inmediata.
   - NUNCA empieces con "Hola a todos", "Bienvenidos" ni frases genéricas.
   - Abre con una pregunta provocadora, una estadística impactante o una \
afirmación que nadie espera.

2. ESPAÑOL NEUTRO, DINÁMICO Y CERCANO
   - Usa "tú" directo, tono entusiasta pero profesional.
   - Lenguaje claro: explica conceptos técnicos de IA con analogías simples.
   - Frases cortas. Ritmo rápido. Cero relleno.

3. LOOPS ABIERTOS (open loops)
   - A mitad del guion, promete revelar algo valioso (el mejor tool, el secreto \
de la noticia, la estrategia que más funciona) antes del final.
   - Esto retiene al espectador hasta el final.

4. INSTRUCCIONES VISUALES FACELESS EN INGLÉS
   - Después de cada bloque de narración, incluye una instrucción visual clara \
para producción (en inglés), usando el formato:
     [SCENE: <descripción visual en inglés, p. ej. "Screen recording of ChatGPT \
writing a business plan, dynamic zoom in on the text being generated"]
   - Las escenas deben ser variadas: demos de herramientas, gráficos animados, \
texto en pantalla, B-roll temático, zoom dinámico, etc.

5. CTA NATURAL Y AFILIADOS
   - Al final, haz una llamada a la acción para suscribirse que se sienta genuina \
(no robótica).
   - Si mencionas herramientas, añade frases de gancho para links de afiliado: \
"link en la descripción", "pruébalo gratis desde el link de abajo".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FORMATO DE SALIDA — JSON ESTRICTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Responde ÚNICAMENTE con JSON válido — sin markdown, sin texto extra.

Schema:
{
  "viral_titles": [
    "<Título viral 1, máx 70 chars, SEO + CTR optimizado>",
    "<Título viral 2>",
    "<Título viral 3>"
  ],
  "thumbnail_concept": "<Descripción de elementos visuales y texto para la \
miniatura (high CTR): colores, expresión, texto overlay, estilo)>",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "<Texto en español que dice el narrador para esta escena>",
      "visual_prompt": "<English description for DALL-E background image: \
photorealistic, cinematic, no text overlays>",
      "duration_seconds": <integer entre 6 y 25>
    }
  ]
}

Reglas del schema:
- viral_titles: exactamente 3 títulos. Emocionales, con número o promesa concreta.
- thumbnail_concept: 2–4 frases describiendo la miniatura ideal.
- scenes: entre 6 y 10 escenas. Primera escena = hook. Última escena = CTA.
- narration: el texto real que se leerá en voz alta, en español.
- visual_prompt: descripción en inglés para DALL-E 3 (sin texto en la imagen).
- duration_seconds: duración estimada leyendo la narración a ritmo natural.
"""


class ScriptWriterAgent:
    """Calls Claude to generate a structured Spanish-language scene-by-scene script."""

    def __init__(self) -> None:
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def run(self, stories: list[dict]) -> dict:
        print("[ScriptWriter] Generating script with Claude...")
        today = date.today().strftime("%B %d, %Y")
        stories_text = "\n\n".join(
            f"## {i+1}. {s['title']} ({s['source']})\n{s['summary']}"
            for i, s in enumerate(stories)
        )
        user_message = (
            f"Hoy es {today}.\n\n"
            f"Aquí están las últimas noticias de IA:\n\n{stories_text}\n\n"
            "Crea un guion de video de 6–10 escenas cubriendo las historias más "
            "relevantes para emprendedores hispanohablantes. "
            "Recuerda: hook explosivo, español neutro, loops abiertos y CTA final."
        )

        response = self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=6000,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )

        raw = next(b.text for b in response.content if b.type == "text")
        script = json.loads(raw)
        self._validate(script)
        title = script["viral_titles"][0]
        print(f"[ScriptWriter] Script ready: '{title}' — {len(script['scenes'])} scenes.")
        return script

    @staticmethod
    def _validate(script: dict) -> None:
        assert "viral_titles" in script and len(script["viral_titles"]) == 3, \
            "Need exactly 3 viral_titles"
        assert "thumbnail_concept" in script, "Missing 'thumbnail_concept'"
        assert "scenes" in script and script["scenes"], "Missing 'scenes'"
        for s in script["scenes"]:
            for key in ("scene_number", "narration", "visual_prompt", "duration_seconds"):
                assert key in s, f"Scene missing '{key}'"
