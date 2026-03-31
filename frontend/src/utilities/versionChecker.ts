interface VersionManifest {
  version: string;
  buildTime?: string;
}

interface VersionMismatchPayload {
  currentVersion: string;
  remoteVersion: string;
  remoteBuildTime?: string;
}

interface StartVersionCheckerOptions {
  checkIntervalMs?: number;
  manifestPath?: string;
  currentVersion?: string;
  onVersionMismatch: (payload: VersionMismatchPayload) => void;
}

const DEFAULT_INTERVAL_MS = 5 * 60 * 1000;

const resolveCurrentVersion = (providedVersion?: string): string => {
  if (providedVersion && providedVersion.trim()) {
    return providedVersion;
  }

  const envVersion = import.meta.env.VITE_APP_VERSION;
  if (typeof envVersion === 'string' && envVersion.trim()) {
    return envVersion;
  }

  return 'unknown';
};

const fetchRemoteVersion = async (manifestPath: string): Promise<VersionManifest | null> => {
  try {
    const separator = manifestPath.includes('?') ? '&' : '?';
    const res = await fetch(`${manifestPath}${separator}t=${Date.now()}`, {
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      },
    });

    if (!res.ok) {
      return null;
    }

    const data = (await res.json()) as Partial<VersionManifest>;
    if (!data.version || typeof data.version !== 'string') {
      return null;
    }

    return {
      version: data.version,
      buildTime: data.buildTime,
    };
  } catch {
    return null;
  }
};

export const startVersionChecker = (options: StartVersionCheckerOptions): (() => void) => {
  const {
    checkIntervalMs = DEFAULT_INTERVAL_MS,
    manifestPath = '/version.json',
    currentVersion,
    onVersionMismatch,
  } = options;

  const appVersion = resolveCurrentVersion(currentVersion);
  let stopped = false;
  let hasNotified = false;

  const check = async () => {
    if (stopped || hasNotified) {
      return;
    }

    const remote = await fetchRemoteVersion(manifestPath);
    if (!remote) {
      return;
    }

    if (remote.version !== appVersion) {
      hasNotified = true;
      onVersionMismatch({
        currentVersion: appVersion,
        remoteVersion: remote.version,
        remoteBuildTime: remote.buildTime,
      });
    }
  };

  void check();

  const timer = window.setInterval(() => {
    void check();
  }, checkIntervalMs);

  return () => {
    stopped = true;
    window.clearInterval(timer);
  };
};
