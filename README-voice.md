# AntBot Voice — README

Deux expériences voice AI sur antbot.dev, même UI, deux stacks différentes.

---

## `/voice/` — AntBot Voice (ElevenLabs)

**Stack :** ElevenLabs Conversational AI + LiveKit  
**Use case :** Agent vocal généraliste, persona AntBot  
**URL prod :** https://antbot.dev/voice/

### Comment ça marche

1. L'utilisateur appuie sur l'orb
2. Le SDK `@11labs/client` ouvre une session WebRTC avec l'agent ElevenLabs
3. Audio bidirectionnel en temps réel via LiveKit
4. Les messages (user + agent) s'affichent dans la zone transcript

### Config

L'`AGENT_ID` est hardcodé dans le HTML :
```
agent_6701km7v5mj1ebj9ptk48t8dtdxf
```
Pour changer l'agent ou le persona → modifier l'ID sur la console ElevenLabs.

### Dépendances CDN
```html
<script src="https://cdn.jsdelivr.net/npm/livekit-client@latest/..."></script>
<script src="https://cdn.jsdelivr.net/npm/@11labs/client@latest/..."></script>
```

---

## `/voice-goog/` — AntBot Phone / Ant Boat 🛳️ (Gemini Live)

**Stack :** Gemini 3.1 Flash Live API (WebSocket natif)  
**Use case :** SDR IA — Sophie, SDR chez Go1 ("Go Ouane"), script de prospection complet  
**URL prod :** https://antbot.dev/voice-goog/  
**Verdict :** Gemini Live > ElevenLabs pour agents temps réel (latence, fluidité, naturel)

### Comment ça marche

1. La page charge la clé API depuis `/voice-goog/config.json` (jamais dans le source)
2. WebSocket ouvert vers `wss://generativelanguage.googleapis.com/ws/...`
3. Setup envoyé : modèle + voix + system prompt Sophie
4. Le micro est capturé, resample 48kHz → 16kHz, envoyé en `audio/pcm` via `realtimeInput.audio`
5. L'audio reçu (24kHz PCM) est décodé et joué via `AudioContext + BufferSource`
6. Transcription input/output affichée en temps réel

### Voix disponibles
`Puck · Charon · Kore · Fenrir · Aoede (défaut) · Orus · Leda · Perseus`

Changer via URL param : `?voice=Kore`

### Config clé API
La clé Google est servie par Caddy depuis la config Caddy :
```
handle /voice-goog/config.json {
    header Content-Type application/json
    respond `{"key":"AIzaSy..."}` 200
}
```
→ Pour changer la clé : modifier le Caddyfile sur le VPS.

### Fixes techniques importants (à conserver)
| Problème | Fix |
|----------|-----|
| Safari iOS blob WebSocket | `await blob.text()` pour parser les messages |
| WS close 1007 | `mediaChunks` deprecated → utiliser `realtimeInput.audio` + `mimeType: "audio/pcm"` |
| WS close 1007 (endpoint) | Utiliser `v1alpha`, pas `v1beta` pour Gemini 3.1 Flash Live |
| Resampling mic Safari | Safari capture à 48kHz → downsample custom vers 16kHz |
| iOS AudioContext bloqué | Initialiser le playback dans un user gesture (click sur l'orb) |

### Persona Sophie — Go1 SDR
System prompt complet dans le HTML. Points clés :
- Prononciation : "Go1" → "Go Ouane" / "Coorpacademy" → "Corp Academy"
- Script en 6 étapes : accroche → opener LinkedIn → capture email → pitch → qualification LMS → RDV
- Gestion objections AQPR (Accepter / Questionner / Preuve / Re-proposer)
- Si IA détectée : assume et continue

---

## Structure des fichiers

```
/var/www/antbot-dev/
├── voice/
│   └── index.html          # ElevenLabs stack
└── voice-goog/
    ├── index.html          # Gemini Live stack (Sophie SDR)
    └── config.json         # Clé API Google (servie par Caddy, jamais commitée)
```

---

## Comparatif

| Critère | `/voice/` (ElevenLabs) | `/voice-goog/` (Gemini Live) |
|---------|----------------------|------------------------------|
| Fluidité | Bonne | ⭐ Excellente |
| Latence | ~500ms | ~100ms |
| Naturalisme | Bon | ⭐ Meilleur |
| Coût | ~$0.30-0.50/conv | Variable (Gemini API) |
| Setup | SDK clé en main | WebSocket custom |
| Voix | Voix ElevenLabs | Voix Google (Aoede, Kore…) |
| Use case | Agent généraliste | ⭐ SDR / temps réel |

**Conclusion :** Gemini Live est clairement supérieur pour les agents conversationnels temps réel. ElevenLabs garde l'avantage sur la qualité vocale des voix pour du TTS classique (podcasts, narration).

---

*Projet Antoine Dumont — antbot.dev*
