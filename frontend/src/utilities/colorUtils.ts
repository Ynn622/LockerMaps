/**
 * 根據站點類型返回對應的顏色
 * @param type 站點類型 (MRT, TRA, OWL 等)
 * @returns 十六進制顏色碼
 */
export const getMarkerColor = (type: string): string => {
    switch (type) {
        case 'MRT': return '#0088FF'; // 藍色 - 捷運
        case 'TRA': return '#6B7280'; // 灰色 - 台鐵
        case 'OWL': return '#e76c2fff' // 橘色 - OWL
        default: return '#6B7280';
    }
};

/**
 * 根據站點類型返回對應的 Tailwind 漸層色類名
 * @param type 站點類型 (MRT, TRA, OWL 等)
 * @returns Tailwind CSS 類名字符串
 */
export const getTypeDisplayClass = (type: string): string => {
    switch (type) {
        case 'MRT': return 'from-green-600 to-blue-500'; // 藍綠色漸層 - 捷運
        case 'TRA': return 'from-gray-600 to-gray-500'; // 灰色漸層 - 台鐵
        case 'OWL': return 'from-orange-600 to-orange-500'; // 橘色漸層 - OWL
        default: return 'from-gray-700 to-gray-600';
    }
};

/**
 * 根據站點類型返回顯示名稱
 * @param type 站點類型 (MRT, TRA, OWL 等)
 * @returns 友好的顯示名稱
 */
export const getTypeDisplayName = (type: string): string => {
    switch (type) {
        case 'MRT': return '捷運寄物櫃';
        case 'TRA': return '台鐵寄物櫃';
        case 'OWL': return 'OWL智慧型寄物櫃';
        default: return type;
    }
};

/**
 * 根據 tag 內容返回對應的顏色類名（用於捷運站代碼）
 * @param tag 標籤內容（例如：BR00, BL00, R00, O00, G00）
 * @returns Tailwind CSS 類名字符串
 */
export const getTagColorClass = (tag: string): string => {
    if (tag.startsWith('BR')) return 'bg-amber-600 text-white'; // 棕色底 - 文湖線
    if (tag.startsWith('BL')) return 'bg-blue-600 text-white'; // 藍色底 - 板南線
    if (tag.startsWith('R')) return 'bg-red-600 text-white'; // 紅色底 - 淡水信義線
    if (tag.startsWith('O')) return 'bg-orange-500 text-white'; // 橘色底 - 中和新蘆線
    if (tag.startsWith('G')) return 'bg-green-700 text-white'; // 綠色底 - 松山新店線
    if (tag.startsWith('Y')) return 'bg-yellow-400 text-white'; // 黃色底 - 環狀線
    if (tag === '桃園捷運') return 'bg-purple-500 text-white'; // 紫色 - 桃園捷運
    if (tag === '台中捷運') return 'bg-green-600 text-white'; // 綠色 - 台中捷運
    return 'bg-white/20 text-white'; // 預設白色半透明
};
