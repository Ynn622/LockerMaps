// API 配置文件

import { logger } from './logger'; // 路徑改成你實際位置

// 切換 API 環境   [ true 為正式環境，false 為地端測試環境 ]
const PROD = true;

// 獲取 API 基礎 URL
export const getApiBaseUrl = () => {
    if (PROD) {
        return `https://ynn22-lockermaps-backend.hf.space`;
    }
    return `http://localhost:7860`;
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * API 呼叫參數介面
 */
export interface CallApiOptions<TBody = any, TParams = Record<string, any>> {
    /** API 端點路徑 */
    url: string;

    /** HTTP 方法 */
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

    /** Query Parameters */
    params?: TParams | null;

    /** Request Body */
    body?: TBody | null;

    /** HTTP Headers */
    headers?: HeadersInit;

    /** Logger 使用的函數名稱 */
    funcName?: string | (() => string);
}

/**
 * 通用 API 呼叫函數
 */
export async function callAPI<TResponse = any>(
    options: CallApiOptions
): Promise<TResponse> {
    const {
        url,
        method = 'GET',
        params = null,
        body = null,
        headers = { 'Content-Type': 'application/json' },
        funcName = 'callAPI'
    } = options;

    const resolvedFuncName =
        typeof funcName === 'function' ? funcName() : funcName;

    try {
        // 記錄 API 開始
        logger.func.start(resolvedFuncName, params ? [params] : []);

        // 構建完整 URL（若已含 http 則不加 base）
        let fullUrl: string = url.startsWith('http')
            ? url
            : `${API_BASE_URL}${url}`;

        // Query Params
        if (params) {
            const searchParams = new URLSearchParams();

            Object.entries(params).forEach(([key, value]) => {
                if (value !== null && value !== undefined) {
                    searchParams.append(key, String(value));
                }
            });

            const queryString = searchParams.toString();
            if (queryString) {
                fullUrl += (fullUrl.includes('?') ? '&' : '?') + queryString;
            }
        }

        // Fetch options
        const fetchOptions: RequestInit = {
            method,
            headers: {
                ...headers
            }
        };

        // Body
        if (body !== null && body !== undefined) {
            fetchOptions.body = JSON.stringify(body);
        }

        // 發送請求
        const response: Response = await fetch(fullUrl, fetchOptions);

        // HTTP Error
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} ${response.statusText}`);
        }

        // JSON 解析
        const data: TResponse = await response.json();

        // 成功記錄
        logger.func.success(resolvedFuncName, params ? [params] : []);

        return data;

    } catch (error) {
        // 錯誤記錄
        logger.func.error(resolvedFuncName, params ? [params] : []);
        logger.error(`${resolvedFuncName} API 錯誤:`, error);

        throw error;
    }
}