// ========================
// Console Logger (TypeScript)
// ========================

/** 是否啟用 log */
let LOG_ENABLED: boolean = true;

/** Log 類型定義 */
type LogType =
    | 'start'
    | 'success'
    | 'error'
    | 'log'
    | 'warn'
    | 'fatal'
    | 'debug';

/** Log 樣式 */
interface LogStyle {
    icon: string;
    tag: string;
}

/** LOG_TYPES 型別安全定義 */
const LOG_TYPES: Record<LogType, LogStyle> = {
    start:   { icon: '🔵', tag: 'Start' },
    success: { icon: '🟢', tag: 'Success' },
    error:   { icon: '🔴', tag: 'Error' },
    log:     { icon: '⚪', tag: 'Log' },
    warn:    { icon: '🟡', tag: 'Warn' },
    fatal:   { icon: '🔴', tag: 'Error' },
    debug:   { icon: '🟣', tag: 'Debug' }
};

/**
 * 格式化時間 (HH:mm:ss.S)
 */
function formatTime(date: Date = new Date()): string {
    const ms: number = Math.floor(date.getMilliseconds() / 100); // 0~9
    return (
        date.toLocaleTimeString('zh-TW', { hour12: false }) + '.' + ms
    );
}

/**
 * 核心 log 函數
 */
function _log(
    type: LogType,
    fn: string | Function,
    params: unknown[] = []
): void {
    if (!LOG_ENABLED) return;

    const { icon, tag } = LOG_TYPES[type] ?? LOG_TYPES.log;

    const fnName: string =
        typeof fn === 'function' ? fn.name || 'anonymous' : fn;

    const paramStr: string = params
        .map(p => {
            try {
                return JSON.stringify(p);
            } catch {
                return '[Circular]';
            }
        })
        .join(', ');

    console.log(
        `${formatTime()} ${icon} [${tag}] ${fnName}(${paramStr})`
    );
}

/**
 * Logger 介面
 */
interface Logger {
    func: Record<
        LogType,
        (fn: string | Function, params?: unknown[]) => void
    >;

    info: (...args: unknown[]) => void;
    warn: (...args: unknown[]) => void;
    error: (...args: unknown[]) => void;
    debug: (...args: unknown[]) => void;
}

/**
 * Logger 實作
 */
export const logger: Logger = {
    func: {} as Logger['func'],

    info: (...args: unknown[]) => {
        if (!LOG_ENABLED) return;
        const { icon, tag } = LOG_TYPES.log;
        console.log(`${formatTime()} ${icon} [${tag}]`, ...args);
    },

    warn: (...args: unknown[]) => {
        if (!LOG_ENABLED) return;
        const { icon, tag } = LOG_TYPES.warn;
        console.warn(`${formatTime()} ${icon} [${tag}]`, ...args);
    },

    error: (...args: unknown[]) => {
        if (!LOG_ENABLED) return;
        const { icon, tag } = LOG_TYPES.fatal;
        console.error(`${formatTime()} ${icon} [${tag}]`, ...args);
    },

    debug: (...args: unknown[]) => {
        if (!LOG_ENABLED) return;
        const { icon, tag } = LOG_TYPES.debug;
        console.log(`${formatTime()} ${icon} [${tag}]`, ...args);
    }
};

/**
 * 動態建立 logger.func.xxx
 */
(Object.keys(LOG_TYPES) as LogType[]).forEach(type => {
    logger.func[type] = (fn, params = []) => _log(type, fn, params);
});