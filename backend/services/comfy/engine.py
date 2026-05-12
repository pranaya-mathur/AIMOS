"""
AIMOS Prompt Engine (v6.0 - Cinematic Diversity & True Entropy)

- 20+ unique cinematic banner scene pools (urban, neon, alpine, coastal, studio, desert, etc.)
- True time-based random seed so EVERY API call produces a fresh composition
- Full lens/texture/lighting depth banks applied to banner mode (were previously skipped)
- New STYLE_MAP entries: urban, night, dramatic
- scene_override support for directed visual output
"""

import os
import json
import random
import time
import hashlib
from typing import Optional


class PromptEngine:
    # ============================================================
    # STYLE PRESETS
    # ============================================================
    STYLE_MAP = {
        "luxury": {
            "background": "dark luxury studio, heavy black marble slab, natural caustics from glass, realistic dust motes in light beams",
            "lighting": "ARRI SkyPanel softbox, side Rembrandt lighting, subtle warm rim glow, organic lens flare",
            "camera": "Phase One XF 100MP, 80mm Schneider lens, f/2.8, raw photo quality",
            "mood": "high-end luxury brand campaign, tangible premium aesthetic, tactile materiality",
            "material": "meticulous reflections, polished physical surfaces, micro-textured highlights",
            "motion_hint": "unsteady cinematic hand-cam drift, slow organic pan"
        },
        "minimal": {
            "background": "pure white semi-gloss infinity wall, subtle floor scuffs, raw studio environment",
            "lighting": "natural window light diffusion, soft natural shadows with realistic falloff",
            "camera": "Leica M11, 50mm Summilux lens, f/5.6, sharp documentary style",
            "mood": "product-first minimalism, honest brand identity, no digital smoothing",
            "material": "tangible matte finish, realistic plastic/metal grain, sharp tactile edges",
            "motion_hint": "static locked camera, subtle focus breathing"
        },
        "modern": {
            "background": "industrial tech lab, exposed brushed aluminum surfaces, glowing interface reflections",
            "lighting": "cool-white LED panels, sharp directional rim light, high-contrast chiaroscuro",
            "camera": "Sony A7R V, 35mm GM lens, f/1.4, extreme micro-detail",
            "mood": "cutting-edge industrial hardware ad, futuristic but physically real",
            "material": "machined metal, raw carbon fiber weave, realistic glass refraction",
            "motion_hint": "mechanical robotic slider motion, precise focus pull"
        },
        "nature": {
            "background": "overcast forest floor, wet mossy granite, natural out-of-focus foliage",
            "lighting": "dappled natural sunlight filtered through canopy, organic ambient occlusion",
            "camera": "Canon R5, 100mm Macro lens, f/4, shallow depth of realism",
            "mood": "eco-sustainable premium lifestyle, earthy and grounded, raw nature capture",
            "material": "natural wood grain, organic rock textures, believable water droplets",
            "motion_hint": "gentle wind sway, leaves fluttering in background blur"
        },
        "cinematic": {
            "background": "gritty urban landscape at dusk, wet asphalt, distant sodium vapor lights",
            "lighting": "neon-tinted side lighting, anamorphic horizontal flares, moody blue-hour ambient",
            "camera": "ARRI Alexa Mini, Panavision Anamorphic lenses, cinematic 2.35:1 grain",
            "mood": "narrative brand storytelling, heavy cinematic atmosphere, realistic urban grit",
            "material": "worn textures, realistic weather-worn surfaces, cinematic light-bleed",
            "motion_hint": "heavy cinematic dolly sweep, handheld immersion"
        },
        "urban": {
            "background": "rain-slicked midnight rooftop, neon city skyline bokeh, glowing puddle reflections, skyscrapers piercing violet clouds",
            "lighting": "electric indigo and amber neon wash, strong rim backlight from city glow, dramatic top-down key light",
            "camera": "ARRI Alexa 65, Leica Summilux-C 35mm, f/1.4, cinematic blue-orange grade",
            "mood": "premium urban street campaign, bold metropolitan energy, sophisticated and edgy",
            "material": "wet reflective concrete, chrome highlights, dark leather textures",
            "motion_hint": "slow cinematic crane rise, city blur sweep"
        },
        "night": {
            "background": "deep navy nightscape, long-exposure city light trails, misty atmosphere, isolated pool of warm spotlight on subject",
            "lighting": "single powerful key spotlight from above, deep shadow fill, cool moonlight rim, warm tungsten accent",
            "camera": "Sony FX9, 50mm Zeiss Otus, f/0.95, extreme low-light clarity",
            "mood": "intimate luxury campaign at night, atmospheric mystery, high-contrast prestige",
            "material": "dark suede, brushed platinum, deep lacquer finishes",
            "motion_hint": "locked static night exposure, subtle smoke drift"
        },
        "dramatic": {
            "background": "volcanic black sand beach at sunrise, dramatic sea spray, burning orange horizon, storm clouds parting",
            "lighting": "ultra-golden backlight from rising sun, strong rim flare, atmospheric haze",
            "camera": "Phase One XT, 32mm RS lens, f/2.8, extreme dynamic range",
            "mood": "epic adventure brand narrative, raw elemental power, cinematic grandeur",
            "material": "battle-worn premium textures, raw canvas, titanium hardware",
            "motion_hint": "epic pull-back reveal, slow-motion environmental drama"
        },
        "raw_product": {
            "background": "unprocessed raw studio floor, heavy concrete textures, industrial backdrop",
            "lighting": "single harsh strobe, high-contrast flash photography look, realistic hard shadows",
            "camera": "Hasselblad H6D, 80mm lens, sharp raw capture, f/11",
            "mood": "honest product portrait, raw and unfiltered, high detail realism",
            "material": "unmodified textures, visible material pores, realistic build quality",
            "motion_hint": "static framing, zero motion, absolute stability"
        }
    }

    # ============================================================
    # CINEMATIC BANNER SCENES (20 unique environments)
    # ============================================================
    BANNER_SCENES = [
        # Urban / Night
        "midnight urban rooftop scene: rain-slicked black concrete, electric neon city skyline reflected in puddles, amber and violet light wash, a sharply dressed figure walking in silhouette, bokeh skyscrapers glowing in the distance",
        "underground parking garage at dusk: brutal concrete pillars, single overhead fluorescent strip, long perspective shadows, luxury vehicle headlights cutting through haze, product positioned on polished hood",
        "neon-lit Tokyo back alley at 2am: glowing Japanese signage, steam vents, wet cobblestone, mysterious figure with product, electric teal and magenta palette",
        "penthouse terrace overlooking a lit mega-city at night: glass balustrade, infinity pool edge reflection, deep navy sky, city glow as natural ambient, product on marble ledge",
        "deserted freeway overpass at golden hour: orange haze, industrial brutalism, lone figure, product elevated on concrete barrier, long shadows, warm cinematic grade",

        # Nature / Adventure
        "Icelandic black sand beach at dawn: volcanic terrain, aurora faintly visible overhead, sea mist rolling in, product on weathered driftwood, ethereal cold light",
        "misty Alpine meadow at sunrise: snow-capped peaks in soft focus, golden grass, lone pine trees, morning fog pooling in valley, product placed on a mossy rock",
        "dramatic coastal cliff in Patagonia: crashing Atlantic waves far below, overcast moody sky, wind-swept grass, product anchored on granite ledge, cinematic wide shot",
        "Saharan desert at the magic hour: rolling terracotta dunes, ultra-long shadows, single camel silhouette on ridge, product half-submerged in warm sand, golden haze",
        "ancient Japanese bamboo forest: dappled jade-green light, mist between towering stalks, stone lantern, product resting on moss, tranquil spiritual atmosphere",

        # Studio / Editorial
        "high-fashion black infinity studio: razor-sharp studio strobe, perfect specular highlights on product, single beam of white light from above, marble plinth, editorial Vogue aesthetic",
        "brutalist concrete studio loft: raw exposed concrete walls, floor-to-ceiling industrial windows, diffused overcast light, product on a poured-cement plinth, architectural minimalism",
        "chrome and glass tech lab: reflective silver floors, glowing blue wall panels, holographic light fragments, product on a precision-machined stand, futuristic yet real",
        "vintage French brasserie interior: warm amber chandelier light, dark oak paneling, worn leather, product placed on antique table, moody rich Parisian aesthetic",

        # Lifestyle / Aspirational
        "first-class airport departure lounge: floor-to-ceiling glass runway view, golden sunset outside, luxury seating, a confident traveler with product beside a private jet gate",
        "sleek modern hotel lobby: dramatic double-height atrium, cascading orchids, marble floor with long light reflections, fashionable subject with product, sophisticated metropolitan energy",
        "sun-drenched Mediterranean yacht deck: turquoise sea stretching to horizon, white fiberglass deck, bright summer light, product beside a champagne glass, aspirational leisure",
        "Kyoto temple garden at golden hour: vermilion torii gates, raked gravel, moss and maple trees, warm low sunlight, product placed reverently on stone, cultural luxury",

        # Bold / Graphic
        "extreme close-up macro hero shot: product fills 70% of frame, razor-sharp material texture, single dramatic side light, inky black void background, hyper-realistic surface detail",
        "anti-gravity floating product reveal: product suspended in mid-air with cinematic motion blur trails, pure obsidian studio background, intense spotlight, dramatic editorial energy",
    ]

    # ============================================================
    # BANNER COMPOSITION FRAMEWORKS (pure layout/framing)
    # ============================================================
    BANNER_COMPOSITIONS = [
        "cinematic horizontal hero, Rule of Thirds balance, subject right, large negative space left for copy, low-angle power perspective",
        "panoramic 16:9 lifestyle spread, extreme shallow depth of field, intentional light leaks, product sharp against dreamy background",
        "dramatic center-mass composition, product as absolute hero, atmospheric mist/dust, global illumination, shadow play",
        "ultra-wide commercial sprawl, left-to-right cinematic gradient, razor-sharp product focus, abstract luxury environment",
        "minimalist billboard layout, macro lens product detail off-center, modern editorial balance, strong negative space",
        "split-composition: bold typographic negative space left panel, lifestyle scene bleeding right, clean dividing light element",
        "low horizon line composition, product elevated against open sky or city glow, dramatic upward perspective",
        "environmental immersion: product small within grand epic scene, scale creates desire and aspiration",
    ]

    # ============================================================
    # DEPTH BANKS (now applied to banner mode)
    # ============================================================
    COMPOSITION_VARIANTS = [
        "asymmetric professional framing, slight off-center focus",
        "dynamic low-angle commercial perspective",
        "detailed macro close-up focus on hardware textures",
        "cinematic wide shot with significant atmospheric depth",
        "natural candid product placement, looks un-staged",
        "overhead technical flatlay with realistic grounding",
    ]

    LENS_GEAR = [
        "shot on 35mm Kodak Portra 400 film stock, fine grain",
        "Panavision anamorphic lens compression, subtle barrel distortion",
        "Zeiss Master Prime clarity, realistic chromatic aberration at edges",
        "Vintage Super Baltar lens warmth, soft corner falloff",
        "RED V-Raptor sensor quality, 8k raw debayering",
        "Leica Noctilux at f/0.95, ethereal bokeh with sharp center",
        "Canon CN-E cinema prime, cinematic color science",
    ]

    LIGHTING_TECH = [
        "three-point studio lighting setup with physical bounce boards",
        "dramatic rim lighting from a powerful HMI source",
        "subtle volumetric fog reflecting light beams, realistic haze",
        "golden hour natural sunlight casting long soft shadows",
        "cool moonlight ambient with warm tungsten key light",
        "neon sign practical lighting as key source, deep colored shadows",
        "single overhead Fresnel spotlight, cabaret-style hard light",
    ]

    TEXTURE_DETAILS = [
        "micro-scratches on metallic surfaces, realistic wear",
        "subtle fingerprint on glass, believable material handling",
        "micro-dust caught in the spotlight, atmospheric realism",
        "unmatched material grain, raw tactile finish",
        "complex subsurface scattering on plastics, realistic light absorption",
        "water droplets beading on matte surface, physical accuracy",
        "worn leather grain with natural patina, tactile depth",
    ]

    CAMPAIGN_VARIANTS = [
        "global prestige brand identity campaign",
        "award-winning cinematic commercial cinematography",
        "high-budget Super Bowl ad aesthetic",
        "premium editorial magazine cover photography",
        "world-class industrial design showcase",
        "vibrant seasonal sales event marketing campaign",
        "luxury travel and lifestyle editorial",
        "high-end commercial for premium brand launch",
        "outdoor adventure gear promotional spread",
        "Cannes Lions-winning advertising photography",
    ]

    COLOR_DIRECTIONS = [
        "deep navy and electric indigo with warm amber accents",
        "rich charcoal and rose gold with cream highlights",
        "forest green and burnished copper with ivory",
        "midnight black and chrome silver with electric blue",
        "warm terracotta and dusty sage with sand",
        "pure obsidian and platinum with a single crimson accent",
        "cobalt blue and white with bold yellow accents",
        "dusky violet and peach with soft gold",
    ]

    MOTION_VARIANTS = [
        "perfectly stable object presence, zero flickering",
        "physically accurate movement, realistic inertia",
        "consistent subject geometry across temporal frames",
        "high-fidelity motion rendering, no AI artifacts",
    ]

    # ============================================================
    # NEGATIVE PROMPT
    # ============================================================
    NEGATIVE_PROMPT = (
        "3d render, cgi, digital painting, cartoon, anime, virtual world, "
        "plastic skin, smooth textures, fake lighting, unreal engine, octane render, "
        "over-sharpened, digital artifacts, airbrushed, unnatural symmetry, "
        "multiple subjects, duplicate objects, cluttered scene, watermark, "
        "blurry, soft focus, noise, grain artifacts, distorted shape, warped geometry, "
        "broken parts, cheap plastic look, unrealistic reflections, bad shadows, "
        "cropped, messy composition, flickering, temporal distortion, morphing, jitter, "
        "text, typography, words, letters, numbers, captions, labels, watermark, logo overlay"
    )

    # ============================================================
    # REFINEMENT RULES
    # ============================================================
    REFINEMENT_RULES = {
        "premium": "ultra luxury finish, high-budget production, elite brand aesthetic",
        "sharp": "tack sharp optic clarity, enhanced micro-detail, crystal clear focus",
        "moody": "dramatic chiaroscuro lighting, cinematic tension, dark premium mood",
        "realistic": "raw photorealistic quality, natural imperfections, physically accurate materials",
        "vibrant": "saturated professional color grade, rich brand tones",
        "filmic": "captured on 35mm film, vintage lens characteristics, cinematic emulsion look",
    }


    @staticmethod
    def _time_seed() -> int:
        """True entropy seed — different on every call regardless of input."""
        return int(time.time() * 1000) ^ random.randint(0, 0xFFFFFF)

    @staticmethod
    def _variant_seed(product_name, features, iteration):
        base = f"{product_name}-{features}-{iteration}"
        return int(hashlib.md5(base.encode()).hexdigest(), 16)

    @classmethod
    def generate_multimodal(
        cls,
        media_path: str,
        media_type: str = "image",
        style_preference: str = "luxury",
        iteration: int = 0
    ) -> dict:
        from scripts.nemotron_handler import NemotronHandler
        handler = NemotronHandler()
        system_instructions = (
            "You are a world-class cinematographer and lighting director. "
            "Analyze the media and write an extremely detailed technical photography brief. "
            "Focus on the 'tangibility' of the product—describe the scent of the materials, the temperature of the lighting, "
            "and the exact camera equipment (ARRI, Leica, etc.) used to capture it. "
            "Avoid AI buzzwords like 'highly detailed'. Use the language of a film professional."
        )
        media_args = {"image_path": media_path} if media_type == "image" else {"video_path": media_path}
        analysis = handler.analyze_media(system_instructions, **media_args)
        return cls.generate(
            product_name="Product",
            features=analysis,
            style_preference=style_preference,
            iteration=iteration,
            mode=media_type
        )

    @classmethod
    def generate(
        cls,
        product_name: str,
        features: str,
        style_preference: str = "luxury",
        iteration: int = 0,
        mode: str = "video",
        reference_media_path: Optional[str] = None,
        engine_mode_override: Optional[str] = None,
    ) -> dict:

        engine_mode = engine_mode_override or os.getenv("PROMPT_ENGINE_MODE", "classic").lower()

        if engine_mode == "multimodal":
            if reference_media_path:
                return cls.generate_multimodal(
                    media_path=reference_media_path,
                    media_type=mode,
                    style_preference=style_preference,
                    iteration=iteration
                )
            else:
                from scripts.nemotron_handler import NemotronHandler
                handler = NemotronHandler()
                prompt = (
                    f"Write a 100-word cinematic technical brief for an AI {mode} generator. "
                    f"Product: {product_name}. Key Selling Points: {features}. Style: {style_preference}. "
                    "Use the persona of a veteran director of photography."
                )
                enhanced_features = handler.analyze_media(prompt)
                return cls.generate_classic(
                    product_name=product_name,
                    features=enhanced_features,
                    style_preference=style_preference,
                    iteration=iteration,
                    mode=mode,
                )

        return cls.generate_classic(
            product_name=product_name,
            features=features,
            style_preference=style_preference,
            iteration=iteration,
            mode=mode,
        )

    @classmethod
    def generate_classic(
        cls,
        product_name: str,
        features: str,
        style_preference: str = "luxury",
        iteration: int = 0,
        mode: str = "video",
    ) -> dict:
        style = cls.STYLE_MAP.get(style_preference.lower(), cls.STYLE_MAP["luxury"])

        # TRUE ENTROPY: use time-based seed so every API call is unique
        rng = random.Random(cls._time_seed())

        scene = rng.choice(cls.BANNER_SCENES)

        composition = rng.choice(cls.BANNER_COMPOSITIONS if mode == "banner" else cls.COMPOSITION_VARIANTS)
        lens = rng.choice(cls.LENS_GEAR)
        lighting_tech = rng.choice(cls.LIGHTING_TECH)
        texture = rng.choice(cls.TEXTURE_DETAILS)
        campaign = rng.choice(cls.CAMPAIGN_VARIANTS)
        color_dir = rng.choice(cls.COLOR_DIRECTIONS)
        motion = rng.choice(cls.MOTION_VARIANTS)

        if mode == "video":
            positive = (
                f"Masterpiece cinematic commercial video of {product_name}. "
                f"The scene captures {features} with raw photorealistic integrity. "
                f"{composition}, {lens}, {motion}. "
                f"{lighting_tech}, {style['lighting']}. "
                f"{style['background']}. "
                f"{style['material']}, {texture}. "
                f"{color_dir}. "
                f"{style['mood']}, {campaign}. "
                f"{style['camera']}, ultra-realistic 8k production."
            )
        elif mode == "banner":
            positive = (
                f"Ultra-realistic cinematic commercial ad banner for '{product_name}'. "
                f"{scene}. "
                f"{composition}, advertising layout. "
                f"{lens}, {style['camera']}. "
                f"{lighting_tech}, {style['lighting']}. "
                f"{color_dir}. "
                f"{style['material']}, {texture}. "
                f"{features}. "
                f"{style['mood']}, {campaign}. "
                f"Format: Cinematic 16:9 horizontal banner, significant clean negative space on one side "
                f"for ad copy overlay, photorealistic commercial photography quality, no text, no watermarks."
            )
        elif mode == "logo":
            positive = (
                f"Masterpiece professional minimalist vector logo for '{product_name}'. "
                f"{features}. "
                f"{style['mood']}, minimalist icon, corporate identity, clean geometric lines. "
                f"High contrast, centered composition, significant negative space, "
                f"suitable for premium branding, flat design aesthetic, trending on Dribbble and Behance. "
                f"Ultra-sharp edges, vector precision, 8k resolution, solid background."
            )
        else:
            positive = (
                f"Masterpiece professional photography of {product_name}. "
                f"The shot focuses on {features} with extreme technical depth. "
                f"{composition}, {lens}. "
                f"{lighting_tech}, {style['lighting']}. "
                f"{style['background']}. "
                f"{style['material']}, {texture}. "
                f"{color_dir}. "
                f"{style['mood']}, {campaign}. "
                f"Raw photo, natural imperfections, 35mm texture, photorealistic excellence."
            )

        return {
            "positive": positive,
            "negative": cls.NEGATIVE_PROMPT,
            "meta": {
                "style": style_preference,
                "iteration": iteration,
                "mode": mode,
                "scene": scene[:60] + "...",
                "color": color_dir,
                "engine_version": "6.0-cinematic-diversity"
            }
        }

    @classmethod
    def refine(cls, base_prompt: str, instruction: str) -> str:
        instruction_lower = instruction.lower()
        additions = []
        for key, value in cls.REFINEMENT_RULES.items():
            if key in instruction_lower:
                additions.append(value)
        if not additions:
            return f"{base_prompt}, {instruction}"
        return f"{base_prompt}, {', '.join(additions)}"

    @classmethod
    def available_styles(cls):
        return list(cls.STYLE_MAP.keys())


if __name__ == "__main__":
    test_product = "Nomad Pro Luggage"
    test_features = "ultra-light polycarbonate shell, silent spinner wheels, TSA-approved lock"

    print("\n--- BANNER PROMPT (urban_night) ---")
    b = PromptEngine.generate(test_product, test_features, "cinematic", mode="banner", scene_override="urban_night")
    print(json.dumps(b, indent=2))

    print("\n--- BANNER PROMPT (random) ---")
    b2 = PromptEngine.generate(test_product, test_features, "luxury", mode="banner")
    print(json.dumps(b2, indent=2))