// 顶部为0度，顺时针计算，并扣除圆盘自身的旋转角度。
export const getPrizeIndex = (x: number, y: number, size: number, rotation: number, count: number) => {
  if (size <= 0 || count <= 0) return -1
  const dx = x - size / 2
  const dy = y - size / 2
  if (dx * dx + dy * dy > (size / 2) * (size / 2)) return -1
  const touchJiaodu = Math.atan2(dx, -dy) * 180 / Math.PI
  const localJiaodu = ((touchJiaodu - rotation) % 360 + 360) % 360
  return Math.min(count - 1, Math.floor(localJiaodu / (360 / count)))
}
