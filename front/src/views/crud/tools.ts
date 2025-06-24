// 防抖函数实现
// export const debounce = (fn: Function, delay: number) => {
//   let timer: number | null = null;
//   return (...args: any[]) => {
//     if (timer) clearTimeout(timer);
//     timer = window.setTimeout(() => {
//       // fn(...args);
//       fn.apply(this, args);
//       timer = null; // 执行后将timer设置为null
//     }, delay);
//   };
// };

// 节流函数实现
// export const throttle = (fn: Function, delay: number) => {
//   let lastTime = 0;
//   return (...args: any[]) => {
//     const now = Date.now();
//     if (now - lastTime >= delay) {
//       // fn(...args);
//       fn.apply(this, args);
//       lastTime = now;
//     }
//   };
// };

// 补零函数
const padZero = (num: number): string => {
  return num < 10 ? `0${num}` : String(num);
};

// 时间戳格式化
export const timestampFormat = (timestamp: number, format = 'yyyy-MM-dd HH:mm:ss'): string => {
  const date = new Date(timestamp);

  // 定义格式化映射
  const formatMap = {
    yyyy: date.getFullYear(),
    MM: padZero(date.getMonth() + 1),
    M: date.getMonth() + 1,
    dd: padZero(date.getDate()),
    d: date.getDate(),
    HH: padZero(date.getHours()),
    H: date.getHours(),
    mm: padZero(date.getMinutes()),
    m: date.getMinutes(),
    ss: padZero(date.getSeconds()),
    s: date.getSeconds(),
  };

  // 替换格式字符串
  return format.replace(/yyyy|MM|M|dd|d|HH|H|mm|m|ss|s/g, (match) => {
    return String(formatMap[match as keyof typeof formatMap]);
  });
};

// 将时间戳转换为 ISO 格式，并调整为本地时区
export function getISOStringWithLocalTimezone(timestamp) {
  const date = new Date(timestamp);

  // 获取时区偏移量（分钟）
  const tzOffset = date.getTimezoneOffset();

  // 调整日期时间
  const adjustedDate = new Date(date.getTime() - tzOffset * 60000);

  // 转换为 ISO 字符串并替换 'Z' 为时区偏移，去掉毫秒部分
  const isoString = adjustedDate.toISOString().replace(/\.\d{3}/, '');
  console.log('@@@isoString', isoString);
  const tzString =
    tzOffset <= 0
      ? `+${String(Math.floor(Math.abs(tzOffset) / 60)).padStart(2, '0')}:${String(
          Math.abs(tzOffset) % 60
        ).padStart(2, '0')}`
      : `-${String(Math.floor(tzOffset / 60)).padStart(2, '0')}:${String(tzOffset % 60).padStart(
          2,
          '0'
        )}`;

  return isoString.replace('Z', tzString);
}
