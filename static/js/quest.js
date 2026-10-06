/**
 * GrassQuest Core Business Logic (Quest Generator, ElevenLabs Audio, History, Sharing)
 */

class QuestManager {
  constructor() {
    this.currentQuest = null;
    this.audioBlobUrl = null;
    this.isMuted = false;
    this.timerInterval = null;
    this.remainingSeconds = 0;
    this.totalDurationSeconds = 0;
    this.isTimerPaused = false;
    this.timeSpentSeconds = 0;
    this.audioPlayer = document.getElementById('globalAudioPlayer');
    this.historyStorageKey = 'grassquest_completed_history_v1';
  }

  /**
   * Request quest generation from the backend open-weight AI (GPT-OSS 20B via Groq).
   */
  async generateQuest({ mood, durationMinutes, questType, locationContext }) {
    const payload = {
      mood: mood,
      duration_minutes: parseInt(durationMinutes, 10),
      quest_type: questType,
      location_context: locationContext || '',
    };

    const response = await fetch('/api/generate-quest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      const errorMsg = data.error || "We couldn't generate your quest right now. Please try again.";
      throw new Error(errorMsg);
    }

    this.currentQuest = data.quest;
    return this.currentQuest;
  }

  /**
   * Fetch synthesized speech from backend ElevenLabs integration.
   * If ElevenLabs is unavailable, falls back gracefully to browser Web Speech API.
   */
  async fetchVoiceAudio(text) {
    if (!text || !text.trim()) return null;

    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        console.warn(`ElevenLabs TTS response status: ${response.status}`);
        return null;
      }

      const blob = await response.blob();
      if (this.audioBlobUrl) {
        URL.revokeObjectURL(this.audioBlobUrl);
      }
      this.audioBlobUrl = URL.createObjectURL(blob);
      return this.audioBlobUrl;
    } catch (err) {
      console.warn('ElevenLabs API request failed, will use fallback speech:', err);
      return null;
    }
  }

  /**
   * Play quest voice instruction using ElevenLabs audio or browser Web Speech API fallback.
   */
  async playVoiceScript(text, onStart, onEnd) {
    if (this.isMuted) {
      console.log('Voice is currently muted by user preference.');
      return;
    }

    // Attempt ElevenLabs audio player first
    if (this.audioBlobUrl && this.audioPlayer) {
      try {
        this.audioPlayer.src = this.audioBlobUrl;
        if (onStart) onStart('elevenlabs');
        this.audioPlayer.onended = () => { if (onEnd) onEnd(); };
        await this.audioPlayer.play();
        return;
      } catch (audioErr) {
        console.warn('Audio element play failed, falling back to Web Speech:', audioErr);
      }
    }

    // Try fetching ElevenLabs audio on the fly if not cached yet
    if (!this.audioBlobUrl) {
      const url = await this.fetchVoiceAudio(text);
      if (url && this.audioPlayer) {
        try {
          this.audioPlayer.src = url;
          if (onStart) onStart('elevenlabs');
          this.audioPlayer.onended = () => { if (onEnd) onEnd(); };
          await this.audioPlayer.play();
          return;
        } catch (playErr) {
          console.warn('Playback error:', playErr);
        }
      }
    }

    // Fallback: Browser Web Speech API
    if ('speechSynthesis' in window && text) {
      try {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        if (onStart) onStart('browser_speech');
        utterance.onend = () => { if (onEnd) onEnd(); };
        window.speechSynthesis.speak(utterance);
      } catch (speechErr) {
        console.warn('Web Speech fallback failed:', speechErr);
      }
    }
  }

  /**
   * Toggle mute state.
   */
  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.isMuted) {
      if (this.audioPlayer) this.audioPlayer.pause();
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    }
    return this.isMuted;
  }

  /**
   * Start the outdoor countdown timer.
   */
  startTimer(durationMinutes, onTick, onComplete) {
    this.stopTimer();
    this.totalDurationSeconds = durationMinutes * 60;
    this.remainingSeconds = this.totalDurationSeconds;
    this.timeSpentSeconds = 0;
    this.isTimerPaused = false;

    this.timerInterval = setInterval(() => {
      if (this.isTimerPaused) return;

      this.remainingSeconds -= 1;
      this.timeSpentSeconds += 1;

      if (onTick) {
        onTick({
          remainingSeconds: this.remainingSeconds,
          timeSpentSeconds: this.timeSpentSeconds,
          formattedRemaining: this.formatTime(this.remainingSeconds),
          progressPercent: Math.min(100, Math.round((this.timeSpentSeconds / this.totalDurationSeconds) * 100)),
        });
      }

      if (this.remainingSeconds <= 0) {
        this.stopTimer();
        if (onComplete) onComplete();
      }
    }, 1000);
  }

  pauseTimer() {
    this.isTimerPaused = true;
    return this.isTimerPaused;
  }

  resumeTimer() {
    this.isTimerPaused = false;
    return this.isTimerPaused;
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  /**
   * Convert seconds to MM:SS string.
   */
  formatTime(seconds) {
    const s = Math.max(0, Math.floor(seconds));
    const mins = Math.floor(s / 60);
    const secs = s % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  /**
   * Format meters into clean km or m string.
   */
  formatDistance(meters) {
    if (meters < 1000) {
      return `${Math.round(meters)} m`;
    }
    return `${(meters / 1000).toFixed(2)} km`;
  }

  /**
   * Save completed quest into localStorage history.
   */
  saveToHistory(quest, timeSpentSeconds, distanceMeters) {
    try {
      const history = this.getHistory();
      const entry = {
        id: 'gq_' + Date.now(),
        title: quest.title || 'Outdoor Mission',
        durationMinutes: Math.max(1, Math.round(timeSpentSeconds / 60)),
        distanceMeters: Math.round(distanceMeters),
        formattedDistance: this.formatDistance(distanceMeters),
        timestamp: new Date().toISOString(),
      };
      history.unshift(entry);
      // Keep only most recent 20 quests
      const trimmed = history.slice(0, 20);
      localStorage.setItem(this.historyStorageKey, JSON.stringify(trimmed));
      return entry;
    } catch (e) {
      console.warn('Could not save to localStorage:', e);
      return null;
    }
  }

  /**
   * Read history from localStorage.
   */
  getHistory() {
    try {
      const raw = localStorage.getItem(this.historyStorageKey);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  /**
   * Clear localStorage history.
   */
  clearHistory() {
    try {
      localStorage.removeItem(this.historyStorageKey);
    } catch (e) {
      console.warn(e);
    }
  }

  /**
   * Web Share API invocation with clipboard fallback.
   */
  async shareQuest(quest, timeSpentMinutes, distanceFormatted) {
    const shareText = `I just completed a GrassQuest:
${quest.title || 'Outdoor Mission'} 🌿
${timeSpentMinutes} minutes outside
${distanceFormatted} walked
AI-generated by GPT-OSS 20B

#TouchGrass #Hacktoberfest`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'GrassQuest - Outdoor Mission Complete 🌿',
          text: shareText,
          url: window.location.origin,
        });
        return { shared: true, method: 'web_share' };
      } catch (err) {
        if (err.name === 'AbortError') {
          return { shared: false, method: 'aborted' };
        }
      }
    }

    // Fallback to Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(shareText);
      return { shared: true, method: 'clipboard' };
    }

    return { shared: false, method: 'unsupported' };
  }
}

window.QuestManager = QuestManager;
