/**
 * GrassQuest GPS Tracker (Browser Geolocation API + Haversine Formula)
 * Calculates real walking distance without third-party paid maps.
 */

class GPSTracker {
  constructor(options = {}) {
    this.options = Object.assign({
      enableHighAccuracy: true,
      maximumAge: 5000,
      timeout: 15000,
      minAccuracyThreshold: 80, // meters, ignore noisy fixes
      minMovementThreshold: 3,  // meters, ignore static GPS drift
    }, options);

    this.watchId = null;
    this.lastPosition = null;
    this.totalDistanceMeters = 0;
    this.isTracking = false;
    this.isSupported = 'geolocation' in navigator;
    this.lastTimestamp = 0;

    this.onUpdateCallback = null;
    this.onErrorCallback = null;
  }

  /**
   * Haversine formula calculates great-circle distance between two coordinates in meters.
   */
  static calculateHaversine(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Earth radius in meters
    const toRad = (deg) => (deg * Math.PI) / 180;

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const phi1 = toRad(lat1);
    const phi2 = toRad(lat2);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(phi1) * Math.cos(phi2) * Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Start tracking user coordinates.
   */
  start(onUpdate, onError) {
    this.onUpdateCallback = onUpdate;
    this.onErrorCallback = onError;

    if (!this.isSupported) {
      if (this.onErrorCallback) {
        this.onErrorCallback('Geolocation is not supported by your browser. Running in non-GPS mode.', false);
      }
      return false;
    }

    this.reset();
    this.isTracking = true;

    try {
      this.watchId = navigator.geolocation.watchPosition(
        (position) => this._handlePosition(position),
        (error) => this._handleError(error),
        {
          enableHighAccuracy: this.options.enableHighAccuracy,
          maximumAge: this.options.maximumAge,
          timeout: this.options.timeout,
        }
      );
      return true;
    } catch (e) {
      console.warn('Could not initialize geolocation watch:', e);
      if (this.onErrorCallback) {
        this.onErrorCallback('Unable to initialize GPS. Continuing without distance tracking.', false);
      }
      return false;
    }
  }

  /**
   * Stop active geolocation watcher.
   */
  stop() {
    if (this.watchId !== null && this.isSupported) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
    this.isTracking = false;
  }

  /**
   * Reset accumulated distance.
   */
  reset() {
    this.totalDistanceMeters = 0;
    this.lastPosition = null;
    this.lastTimestamp = 0;
  }

  /**
   * Internal handler for new GPS coordinates.
   */
  _handlePosition(position) {
    if (!this.isTracking) return;

    const coords = position.coords;
    const accuracy = coords.accuracy || 999;
    const now = position.timestamp || Date.now();

    // Reject low accuracy readings that would distort distance calculation
    if (accuracy > this.options.minAccuracyThreshold) {
      console.log(`[GPS] Skipping reading with low accuracy (${Math.round(accuracy)}m)`);
      if (this.onUpdateCallback) {
        this.onUpdateCallback({
          distanceMeters: this.totalDistanceMeters,
          currentAccuracy: accuracy,
          isLowAccuracy: true,
        });
      }
      return;
    }

    if (this.lastPosition) {
      const delta = GPSTracker.calculateHaversine(
        this.lastPosition.latitude,
        this.lastPosition.longitude,
        coords.latitude,
        coords.longitude
      );

      const timeDeltaSeconds = (now - this.lastTimestamp) / 1000;

      // Basic sanity checks:
      // 1. Must exceed minimum movement threshold to avoid GPS drift while stationary
      // 2. Walking speed check (ignore impossibly fast jumps > 15 m/s unless prolonged)
      const speedEstimate = timeDeltaSeconds > 0 ? delta / timeDeltaSeconds : 0;
      if (delta >= this.options.minMovementThreshold && speedEstimate < 15) {
        this.totalDistanceMeters += delta;
      }
    }

    this.lastPosition = {
      latitude: coords.latitude,
      longitude: coords.longitude,
    };
    this.lastTimestamp = now;

    if (this.onUpdateCallback) {
      this.onUpdateCallback({
        distanceMeters: this.totalDistanceMeters,
        currentAccuracy: accuracy,
        isLowAccuracy: false,
        latitude: coords.latitude,
        longitude: coords.longitude,
      });
    }
  }

  /**
   * Internal handler for geolocation errors.
   */
  _handleError(error) {
    let friendlyMessage = 'Location access is unavailable.';
    let isFatal = false;

    switch (error.code) {
      case error.PERMISSION_DENIED:
        friendlyMessage = "Location access denied. You can continue your quest without GPS distance tracking.";
        isFatal = true;
        this.stop();
        break;
      case error.POSITION_UNAVAILABLE:
        friendlyMessage = "GPS position unavailable. Continuing quest timer and checklist.";
        break;
      case error.TIMEOUT:
        friendlyMessage = "GPS signal timed out. Waiting for connection...";
        break;
      default:
        friendlyMessage = "GPS tracking paused. You can still complete your outdoor quest.";
        break;
    }

    if (this.onErrorCallback) {
      this.onErrorCallback(friendlyMessage, isFatal);
    }
  }
}

// Make GPSTracker available globally
window.GPSTracker = GPSTracker;
