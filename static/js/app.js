/**
 * GrassQuest Application Controller
 * Handles user interactions, 5-step transitions, confetti, and toast alerts.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Instances
  const questManager = new QuestManager();
  const gpsTracker = new GPSTracker();

  // Step Elements
  const steps = {
    landing: document.getElementById('stepLanding'),
    setup: document.getElementById('stepSetup'),
    loading: document.getElementById('stepLoading'),
    result: document.getElementById('stepResult'),
    active: document.getElementById('stepActive'),
    complete: document.getElementById('stepComplete'),
  };

  // Rotating loading phrases
  const loadingPhrases = [
    'Finding a reason to leave your chair…',
    'Analyzing neighborhood walking physics…',
    'Asking open-weight AI for fresh air ideas…',
    'Locating unusual textures and quiet trees…',
    'Drafting instructions for your pocket…',
  ];
  let loadingInterval = null;

  // Active Quest State
  let currentActiveQuest = null;
  let accumulatedDistance = 0;
  let isQuestPaused = false;

  // Confetti Animation State
  let confettiAnimFrame = null;

  // -------------------------------------------------------------------------
  // Navigation / Step Switching
  // -------------------------------------------------------------------------
  function showStep(stepName) {
    Object.values(steps).forEach((el) => {
      if (el) el.classList.remove('active-step');
    });

    if (steps[stepName]) {
      steps[stepName].classList.add('active-step');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // -------------------------------------------------------------------------
  // Toast Notifications
  // -------------------------------------------------------------------------
  function showToast(message, type = 'info', duration = 3800) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✓';
    if (type === 'warning') icon = '⚠️';
    if (type === 'error') icon = '✕';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 250ms ease';
      setTimeout(() => toast.remove(), 260);
    }, duration);
  }

  // -------------------------------------------------------------------------
  // Loading Animation Phrases
  // -------------------------------------------------------------------------
  function startLoadingAnimation() {
    const textEl = document.getElementById('loadingDynamicText');
    let idx = 0;
    if (textEl) textEl.textContent = loadingPhrases[0];

    loadingInterval = setInterval(() => {
      idx = (idx + 1) % loadingPhrases.length;
      if (textEl) {
        textEl.style.opacity = '0';
        setTimeout(() => {
          textEl.textContent = loadingPhrases[idx];
          textEl.style.opacity = '1';
        }, 180);
      }
    }, 2200);
  }

  function stopLoadingAnimation() {
    if (loadingInterval) {
      clearInterval(loadingInterval);
      loadingInterval = null;
    }
  }

  // -------------------------------------------------------------------------
  // Confetti Particle System
  // -------------------------------------------------------------------------
  function triggerConfetti() {
    const canvas = document.getElementById('confettiCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = canvas.parentElement.offsetHeight;

    const particles = [];
    const colors = ['#22c55e', '#4ade80', '#10b981', '#fbbf24', '#f8fafc'];

    for (let i = 0; i < 65; i++) {
      particles.push({
        x: canvas.width / 2,
        y: canvas.height * 0.4,
        vx: (Math.random() - 0.5) * 8,
        vy: (Math.random() - 0.8) * 10,
        size: Math.random() * 6 + 3,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 8,
        opacity: 1,
      });
    }

    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let alive = false;

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.22; // gravity
        p.rotation += p.rotSpeed;
        p.opacity -= 0.009;

        if (p.opacity > 0) {
          alive = true;
          ctx.save();
          ctx.translate(p.x, p.y);
          ctx.rotate((p.rotation * Math.PI) / 180);
          ctx.globalAlpha = Math.max(0, p.opacity);
          ctx.fillStyle = p.color;
          ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
          ctx.restore();
        }
      });

      if (alive) {
        confettiAnimFrame = requestAnimationFrame(render);
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }

    if (confettiAnimFrame) cancelAnimationFrame(confettiAnimFrame);
    render();
  }

  // -------------------------------------------------------------------------
  // Populate Quest Result Card
  // -------------------------------------------------------------------------
  function renderQuestResult(quest) {
    document.getElementById('resultDuration').textContent = `${quest.duration_minutes} MIN`;
    document.getElementById('resultDistance').textContent = `~${questManager.formatDistance(quest.distance_target_meters)}`;
    document.getElementById('resultTitle').textContent = quest.title;
    document.getElementById('resultSummary').textContent = quest.summary;
    document.getElementById('resultObjective').textContent = quest.objective;
    document.getElementById('resultBonus').textContent = quest.bonus;
    document.getElementById('resultSafety').textContent = quest.safety_note;
    document.getElementById('resultVoiceScript').textContent = `“${quest.voice_script}”`;

    // Populate steps list
    const stepsListEl = document.getElementById('resultStepsList');
    stepsListEl.innerHTML = '';
    quest.steps.forEach((stepText) => {
      const li = document.createElement('li');
      li.className = 'step-item';
      li.innerHTML = `<span class="step-marker">✓</span> <span>${stepText}</span>`;
      stepsListEl.appendChild(li);
    });

    // Reset voice preview status
    const voiceStatusText = document.getElementById('voiceStatusText');
    const previewBtn = document.getElementById('previewVoiceBtn');
    if (voiceStatusText) voiceStatusText.textContent = 'Voice ready';
    if (previewBtn) previewBtn.disabled = false;
  }

  // -------------------------------------------------------------------------
  // Active Quest Mode
  // -------------------------------------------------------------------------
  function startActiveQuest(quest) {
    currentActiveQuest = quest;
    accumulatedDistance = 0;
    isQuestPaused = false;

    // Set UI initial values
    document.getElementById('activeMissionName').textContent = quest.title;
    document.getElementById('activeMissionBrief').textContent = quest.objective;
    document.getElementById('activeTargetVal').textContent = questManager.formatDistance(quest.distance_target_meters);
    document.getElementById('activeDistanceVal').textContent = '0.00 km';
    document.getElementById('activeProgressFill').style.width = '0%';
    document.getElementById('activeProgressPct').textContent = '0% of target distance';
    document.getElementById('pauseActiveBtn').textContent = '⏸ Pause';

    showStep('active');

    // 1. Play concise voice guidance immediately
    const startScript = quest.voice_script || 
      `Your GrassQuest has started. You have ${quest.duration_minutes} minutes. Put your phone in your pocket and start walking.`;
    
    questManager.playVoiceScript(
      startScript,
      () => {
        const audioTag = document.getElementById('activeAudioTag');
        if (audioTag) audioTag.textContent = '🎧 Voice: Playing';
      },
      () => {
        const audioTag = document.getElementById('activeAudioTag');
        if (audioTag) audioTag.textContent = '🎧 Put Phone Away';
      }
    );

    // 2. Start Countdown Timer
    questManager.startTimer(
      quest.duration_minutes,
      (tick) => {
        const timerEl = document.getElementById('activeTimer');
        if (timerEl) timerEl.textContent = tick.formattedRemaining;
      },
      () => {
        // Timer completed!
        showToast('Quest time finished! Returning to base.', 'success');
        finishActiveQuest();
      }
    );

    // 3. Start GPS tracking with graceful fallback
    const gpsStarted = gpsTracker.start(
      (update) => {
        accumulatedDistance = update.distanceMeters || 0;
        updateActiveTelemetry(accumulatedDistance, quest.distance_target_meters, update.currentAccuracy);
      },
      (errorMsg, isFatal) => {
        const accLabel = document.getElementById('activeGpsAccuracy');
        if (accLabel) {
          accLabel.textContent = isFatal ? '⚠️ Non-GPS Mode' : '🛰️ Calibrating GPS...';
          accLabel.style.color = isFatal ? '#f59e0b' : '#94a3b8';
        }
        showToast(errorMsg, isFatal ? 'warning' : 'info');
      }
    );

    if (!gpsStarted) {
      const accLabel = document.getElementById('activeGpsAccuracy');
      if (accLabel) {
        accLabel.textContent = '⚠️ Non-GPS Mode';
        accLabel.style.color = '#f59e0b';
      }
    }
  }

  function updateActiveTelemetry(distanceMeters, targetMeters, accuracy) {
    const distEl = document.getElementById('activeDistanceVal');
    const fillEl = document.getElementById('activeProgressFill');
    const pctEl = document.getElementById('activeProgressPct');
    const accEl = document.getElementById('activeGpsAccuracy');

    if (distEl) distEl.textContent = questManager.formatDistance(distanceMeters);

    const percent = Math.min(100, Math.round((distanceMeters / targetMeters) * 100));
    if (fillEl) fillEl.style.width = `${percent}%`;
    if (pctEl) pctEl.textContent = `${percent}% of target distance`;

    if (accEl && accuracy) {
      accEl.textContent = `🛰️ GPS Active (±${Math.round(accuracy)}m)`;
      accEl.style.color = '#4ade80';
    }

    // Auto-complete if target reached
    if (distanceMeters >= targetMeters && percent >= 100) {
      showToast('Distance target reached! Fantastic job!', 'success');
    }
  }

  // -------------------------------------------------------------------------
  // Finish Active Quest
  // -------------------------------------------------------------------------
  function finishActiveQuest() {
    gpsTracker.stop();
    const timeSpentSecs = questManager.timeSpentSeconds || 60;
    questManager.stopTimer();

    const quest = currentActiveQuest;
    if (!quest) return;

    // Save to local history
    questManager.saveToHistory(quest, timeSpentSecs, accumulatedDistance);
    renderHistoryDrawer();

    // Populate completion screen
    const timeMins = Math.max(1, Math.round(timeSpentSecs / 60));
    const distFormatted = questManager.formatDistance(accumulatedDistance);

    document.getElementById('completeQuestTitle').textContent = quest.title;
    document.getElementById('completeTimeSpent').textContent = `${timeMins} min`;
    document.getElementById('completeDistanceWalked').textContent = distFormatted;

    showStep('complete');
    triggerConfetti();

    // Play completion congratulatory voice
    const completionScript = "Quest complete. You successfully escaped the screen. Nice work.";
    questManager.playVoiceScript(completionScript);
  }

  // -------------------------------------------------------------------------
  // Local History Drawer Rendering
  // -------------------------------------------------------------------------
  function renderHistoryDrawer() {
    const listEl = document.getElementById('historyList');
    if (!listEl) return;

    const history = questManager.getHistory();
    if (!history || history.length === 0) {
      listEl.innerHTML = `
        <div class="empty-history">
          <span class="empty-icon">🌱</span>
          <p>No quests logged yet.<br>Complete your first mission to touch grass!</p>
        </div>`;
      return;
    }

    listEl.innerHTML = '';
    history.forEach((item) => {
      const dateStr = new Date(item.timestamp).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      });
      const div = document.createElement('div');
      div.className = 'history-item';
      div.innerHTML = `
        <div class="history-item-title">${item.title} 🌿</div>
        <div class="history-item-meta">
          <span>${item.durationMinutes} min • ${item.formattedDistance}</span>
          <span>${dateStr}</span>
        </div>`;
      listEl.appendChild(div);
    });
  }

  function toggleHistoryDrawer(open) {
    const drawer = document.getElementById('historyDrawer');
    const overlay = document.getElementById('drawerOverlay');
    if (!drawer || !overlay) return;

    if (open) {
      renderHistoryDrawer();
      drawer.classList.add('open');
      overlay.classList.add('open');
      drawer.setAttribute('aria-hidden', 'false');
    } else {
      drawer.classList.remove('open');
      overlay.classList.remove('open');
      drawer.setAttribute('aria-hidden', 'true');
    }
  }

  // -------------------------------------------------------------------------
  // Event Bindings
  // -------------------------------------------------------------------------

  // Landing CTA
  const startPlanningBtn = document.getElementById('startPlanningBtn');
  if (startPlanningBtn) {
    startPlanningBtn.addEventListener('click', () => showStep('setup'));
  }

  // Brand link
  const brandHomeLink = document.getElementById('brandHomeLink');
  if (brandHomeLink) {
    brandHomeLink.addEventListener('click', (e) => {
      e.preventDefault();
      showStep('landing');
    });
  }

  // Back button on setup screen
  const setupBackBtn = document.getElementById('setupBackBtn');
  if (setupBackBtn) {
    setupBackBtn.addEventListener('click', () => showStep('landing'));
  }

  // Form Submission -> Generate Quest
  const questSetupForm = document.getElementById('questSetupForm');
  if (questSetupForm) {
    questSetupForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(questSetupForm);
      const mood = formData.get('mood') || 'Bored';
      const duration = formData.get('duration') || '20';
      const questType = formData.get('quest_type') || 'Explore';
      const locationContext = (formData.get('location_context') || '').trim();

      showStep('loading');
      startLoadingAnimation();

      try {
        const quest = await questManager.generateQuest({
          mood,
          durationMinutes: duration,
          questType,
          locationContext,
        });

        // Prefetch voice audio in background
        if (quest.voice_script) {
          questManager.fetchVoiceAudio(quest.voice_script).catch(() => {});
        }

        renderQuestResult(quest);
        showStep('result');
      } catch (err) {
        console.error('Quest generation failed:', err);
        showStep('setup');
        showToast(err.message || "We couldn't generate your quest right now. Please try again.", 'error', 5000);
      } finally {
        stopLoadingAnimation();
      }
    });
  }

  // Preview Voice Button on Result Screen
  const previewVoiceBtn = document.getElementById('previewVoiceBtn');
  if (previewVoiceBtn) {
    previewVoiceBtn.addEventListener('click', () => {
      if (!questManager.currentQuest) return;
      const script = questManager.currentQuest.voice_script;
      const previewText = document.getElementById('previewVoiceIcon');
      if (previewText) previewText.textContent = '🔊 Playing...';

      questManager.playVoiceScript(
        script,
        () => {},
        () => {
          if (previewText) previewText.textContent = '▶ Listen';
        }
      );
    });
  }

  // Start Quest Button
  const startActiveQuestBtn = document.getElementById('startActiveQuestBtn');
  if (startActiveQuestBtn) {
    startActiveQuestBtn.addEventListener('click', () => {
      if (questManager.currentQuest) {
        startActiveQuest(questManager.currentQuest);
      }
    });
  }

  // Generate Another Button
  const generateAnotherBtn = document.getElementById('generateAnotherBtn');
  if (generateAnotherBtn) {
    generateAnotherBtn.addEventListener('click', () => {
      // Trigger form submit again
      if (questSetupForm) {
        questSetupForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    });
  }

  // Back to Setup Button
  const backToSetupBtn = document.getElementById('backToSetupBtn');
  if (backToSetupBtn) {
    backToSetupBtn.addEventListener('click', () => showStep('setup'));
  }

  // Pause / Resume Active Quest Button
  const pauseActiveBtn = document.getElementById('pauseActiveBtn');
  if (pauseActiveBtn) {
    pauseActiveBtn.addEventListener('click', () => {
      if (!isQuestPaused) {
        questManager.pauseTimer();
        isQuestPaused = true;
        pauseActiveBtn.textContent = '▶ Resume';
        showToast('Quest paused. Enjoy the moment!', 'info');
      } else {
        questManager.resumeTimer();
        isQuestPaused = false;
        pauseActiveBtn.textContent = '⏸ Pause';
        showToast('Quest resumed.', 'info');
      }
    });
  }

  // Replay Voice Guidance Active Button
  const replayVoiceActiveBtn = document.getElementById('replayVoiceActiveBtn');
  if (replayVoiceActiveBtn) {
    replayVoiceActiveBtn.addEventListener('click', () => {
      if (currentActiveQuest && currentActiveQuest.voice_script) {
        questManager.playVoiceScript(currentActiveQuest.voice_script);
      }
    });
  }

  // Complete Quest Button
  const completeQuestBtn = document.getElementById('completeQuestBtn');
  if (completeQuestBtn) {
    completeQuestBtn.addEventListener('click', () => {
      finishActiveQuest();
    });
  }

  // Share Quest Button
  const shareQuestBtn = document.getElementById('shareQuestBtn');
  if (shareQuestBtn) {
    shareQuestBtn.addEventListener('click', async () => {
      if (!currentActiveQuest) return;
      const timeMins = Math.max(1, Math.round(questManager.timeSpentSeconds / 60));
      const distFormatted = questManager.formatDistance(accumulatedDistance);

      const result = await questManager.shareQuest(currentActiveQuest, timeMins, distFormatted);
      if (result.shared) {
        if (result.method === 'clipboard') {
          showToast('Quest summary copied to clipboard! 📋', 'success');
        } else {
          showToast('Quest shared successfully! 🌿', 'success');
        }
      }
    });
  }

  // Create Another Quest from Completion Screen
  const createAnotherQuestBtn = document.getElementById('createAnotherQuestBtn');
  if (createAnotherQuestBtn) {
    createAnotherQuestBtn.addEventListener('click', () => showStep('setup'));
  }

  // Go Home Button from Completion Screen
  const goHomeBtn = document.getElementById('goHomeBtn');
  if (goHomeBtn) {
    goHomeBtn.addEventListener('click', () => showStep('landing'));
  }

  // Sound / Mute Toggle in Header
  const soundToggleBtn = document.getElementById('soundToggleBtn');
  const soundIcon = document.getElementById('soundIcon');
  if (soundToggleBtn) {
    soundToggleBtn.addEventListener('click', () => {
      const isMuted = questManager.toggleMute();
      if (soundIcon) soundIcon.textContent = isMuted ? '🔇' : '🔊';
      showToast(isMuted ? 'Voice audio muted' : 'Voice audio unmuted', 'info');
    });
  }

  // History Drawer Open / Close
  const openHistoryBtn = document.getElementById('openHistoryBtn');
  const closeHistoryBtn = document.getElementById('closeHistoryBtn');
  const drawerOverlay = document.getElementById('drawerOverlay');
  const clearHistoryBtn = document.getElementById('clearHistoryBtn');

  if (openHistoryBtn) {
    openHistoryBtn.addEventListener('click', () => toggleHistoryDrawer(true));
  }
  if (closeHistoryBtn) {
    closeHistoryBtn.addEventListener('click', () => toggleHistoryDrawer(false));
  }
  if (drawerOverlay) {
    drawerOverlay.addEventListener('click', () => toggleHistoryDrawer(false));
  }
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', () => {
      questManager.clearHistory();
      renderHistoryDrawer();
      showToast('Quest log cleared', 'info');
    });
  }
});
