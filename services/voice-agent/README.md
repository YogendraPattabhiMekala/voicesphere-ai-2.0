# LiveKit voice worker (provider-backed)

This worker is now implemented against LiveKit Agents 1.8.11 APIs and the pinned Deepgram/OpenAI/Cartesia/Silero plugins. Versions were checked against the published package index at build time and the quickstart/model examples at `https://docs.livekit.io/agents/start/voice-ai/`, `https://docs.livekit.io/agents/models/stt/deepgram/`, `https://docs.livekit.io/agents/models/llm/openai/`, and `https://docs.livekit.io/agents/models/tts/cartesia/`.

Install `requirements.txt`, export `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `DEEPGRAM_API_KEY`, `OPENAI_API_KEY`, and `CARTESIA_API_KEY`, plus `CARTESIA_VOICE_ID`, then run `python agent.py dev` (or `start` for deployment). The frontend requests a scoped room token and, when API `VOICE_MODE=livekit`, connects and enables the user's microphone. A real call requires the worker process to be running and agent dispatch/routing to match your LiveKit setup. This path has not been exercised with credentials in this environment.

The worker deliberately has no write-capable business tools yet; it will not state that identity checks or order/ticket/handoff actions happened. Audio recording is not configured.
