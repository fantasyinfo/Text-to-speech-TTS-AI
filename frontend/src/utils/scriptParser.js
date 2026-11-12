/**
 * Smart Script Parser & Emotion Detector for Studio View
 * Parses bracketed scripts:
 *   [Narrator – Calm, descriptive, storytelling]
 *   दोपहर का 1 बजा है। प्रिया की desk पर मम्मी का बनाया गरमागरम टिफिन रखा है।
 *
 *   [Curious, suspenseful]
 *   लेकिन तभी उसके फोन पर एक notification आया...
 */

export const EMOTION_SYNONYMS = {
  narrator: 'storytelling',
  narration: 'storytelling',
  descriptive: 'storytelling',
  storytelling: 'storytelling',
  conversational: 'conversational',
  reflective: 'reflective',
  inspirational: 'inspirational',
  urgent: 'urgent',
  secretive: 'secretive',
  emotional: 'emotional',
  serious: 'serious',
  laughing: 'laughing',
  crying: 'crying',
  shouting: 'shouting',
  whispering: 'whispering',
  suspenseful: 'suspenseful',
  suspense: 'suspenseful',
  dramatic: 'dramatic',
  calm: 'calm',
  peaceful: 'peaceful',
  relaxed: 'relaxed',
  serene: 'serene',
  patient: 'patient',
  content: 'content',
  meditative: 'meditative',
  casual: 'relaxed',
  careless: 'relaxed',
  chill: 'relaxed',
  curious: 'curious',
  intrigued: 'intrigued',
  interested: 'interested',
  inquisitive: 'inquisitive',
  wondering: 'wondering',
  skeptical: 'skeptical',
  happy: 'happy',
  joyful: 'joyful',
  excited: 'excited',
  delighted: 'delighted',
  amused: 'amused',
  playful: 'playful',
  proud: 'proud',
  hopeful: 'hopeful',
  grateful: 'grateful',
  relieved: 'relieved',
  promotional: 'motivational',
  energetic: 'excited',
  upbeat: 'happy',
  sad: 'sad',
  heartbroken: 'heartbroken',
  disappointed: 'disappointed',
  lonely: 'lonely',
  hurt: 'hurt',
  melancholic: 'melancholic',
  grief: 'grief_stricken',
  tearful: 'tearful',
  angry: 'angry',
  furious: 'furious',
  irritated: 'irritated',
  frustrated: 'frustrated',
  annoyed: 'annoyed',
  sarcastic: 'sarcastic',
  afraid: 'afraid',
  terrified: 'terrified',
  scared: 'scared',
  anxious: 'anxious',
  nervous: 'nervous',
  panicked: 'panicked',
  surprised: 'surprised',
  shocked: 'shocked',
  astonished: 'astonished',
  amazed: 'amazed',
  stunned: 'stunned',
  confident: 'confident',
  assertive: 'assertive',
  authoritative: 'authoritative',
  motivational: 'motivational'
}

/**
 * Matches a raw emotion string to a valid emotion key
 */
export function matchEmotionKey(raw, emotionsGuide = {}, fallback = 'storytelling') {
  if (!raw || !raw.trim()) return fallback

  const clean = raw.toLowerCase().replace(/[,;/\\-]/g, ' ')
  const words = clean.split(/\s+/).filter(Boolean)

  // 1. Direct match in emotions guide
  for (const w of words) {
    if (emotionsGuide[w]) return w
  }

  // 2. Direct match in synonyms
  for (const w of words) {
    if (EMOTION_SYNONYMS[w]) {
      const syn = EMOTION_SYNONYMS[w]
      if (emotionsGuide[syn] || syn) return syn
    }
  }

  // 3. Substring match
  for (const w of words) {
    if (w.length >= 4) {
      for (const k of Object.keys(emotionsGuide)) {
        if (k.includes(w) || w.includes(k)) return k
      }
    }
  }

  return fallback
}

/**
 * Checks if a string contains bracketed scene cues like [Narrator - Calm]
 */
export function hasBracketScenes(text) {
  if (!text) return false
  return /\[([^\]]+)\]\s*([^\[]+)/.test(text)
}

/**
 * Parses script text into scene objects
 */
export function parseScriptToScenes(
  text,
  defaultVoice = '',
  defaultEmotion = 'storytelling',
  emotionsGuide = {},
  availableVoices = []
) {
  if (!text || !text.trim()) return []

  const pattern = /\[([^\]]+)\]\s*([^\[]+)/g
  const matches = [...text.matchAll(pattern)]

  if (matches.length === 0) {
    return [
      {
        id: 'scene_1',
        index: 1,
        sceneTitle: 'Scene 01',
        speakerRaw: '',
        emotionRaw: defaultEmotion,
        voice: defaultVoice,
        emotion: defaultEmotion,
        text: text.trim()
      }
    ]
  }

  const scenes = []
  let currentVoice = defaultVoice

  matches.forEach((m, idx) => {
    const tag = (m[1] || '').trim()
    const content = (m[2] || '').trim()
    if (!content) return

    let speaker = null
    let emotionStr = tag

    const seps = ['–', '—', '-', ':']
    for (const sep of seps) {
      if (tag.includes(sep)) {
        const parts = tag.split(sep)
        const spkPart = parts[0].trim()
        const emoPart = parts.slice(1).join(sep).trim()
        if (spkPart.length > 0 && emoPart.length > 0) {
          speaker = spkPart
          emotionStr = emoPart
          break
        }
      }
    }

    const matchedEmotion = matchEmotionKey(emotionStr, emotionsGuide, defaultEmotion)

    let sceneVoice = currentVoice || defaultVoice
    if (speaker && availableVoices.length > 0) {
      const spkLower = speaker.toLowerCase()
      const found = availableVoices.find((v) => v.toLowerCase().includes(spkLower))
      if (found) {
        sceneVoice = found
        currentVoice = found
      }
    }

    scenes.push({
      id: `scene_${idx + 1}_${Date.now()}`,
      index: idx + 1,
      sceneTitle: `Scene ${String(idx + 1).padStart(2, '0')}`,
      speakerRaw: speaker || '',
      emotionRaw: emotionStr,
      voice: sceneVoice,
      emotion: matchedEmotion,
      text: content
    })
  })

  return scenes
}

/**
 * Formats scenes back into standard script text with brackets
 */
export function formatScenesToScript(scenes = []) {
  if (!scenes || scenes.length === 0) return ''

  return scenes
    .map((sc) => {
      const spk =
        sc.speakerRaw ||
        (sc.voice || '')
          .split('[')[0]
          .replace('🎭 Custom:', '')
          .replace('🎙️ Preset:', '')
          .trim()

      const emo = (sc.emotion || sc.emotionRaw || 'storytelling')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())

      let header = `[${emo}]`
      if (spk && !['damien black', 'default'].includes(spk.toLowerCase())) {
        header = `[${spk} – ${emo}]`
      }

      return `${header}\n${(sc.text || '').trim()}`
    })
    .join('\n\n')
}

