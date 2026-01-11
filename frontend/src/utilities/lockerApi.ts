// 置物櫃 API 服務

import { callAPI } from './apiConfig';

/**
 * 置物櫃詳細資訊
 */
export interface LockerDetail {
    /** 位置 */
    loc: string;
    /** ID */
    id: number;
    /** 價格 */
    price: string;
    /** 尺寸 */
    size: string;
    /** 空櫃數 */
    empty: number;
    /** 總櫃數 */
    total: number | null;
}

/**
 * 站點資料
 */
export interface StationData {
    /** 站點名稱 */
    station: string;
    /** 類型 */
    type: 'MRT' | 'TRA' | 'OWL';
    /** 標籤 */
    tag: string[];
    /** 置物櫃詳細資訊列表 */
    details: LockerDetail[];
    /** 緯度 */
    lat?: number;
    /** 經度 */
    lng?: number;
}

/**
 * 取得置物櫃資料
 * @param type 類型篩選 (可選): MRT, TRA, OWL
 */
export async function getLockerData(type?: string): Promise<StationData[]> {
    return callAPI<StationData[]>({
        url: '/Locker',
        method: 'GET',
        params: type ? { type } : null,
        funcName: 'getLockerData'
    });
}
