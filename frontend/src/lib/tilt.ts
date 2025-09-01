export function tilt(node: HTMLElement, maxDeg = 2) {
  function onMove(e: MouseEvent) {
    const rect = node.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    const dx = (e.clientX - cx) / (rect.width / 2)
    const dy = (e.clientY - cy) / (rect.height / 2)
    const rx = Math.max(Math.min(-dy * maxDeg, maxDeg), -maxDeg)
    const ry = Math.max(Math.min(dx * maxDeg, maxDeg), -maxDeg)
    node.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg)`
  }
  function reset() { node.style.transform = '' }
  node.addEventListener('mousemove', onMove)
  node.addEventListener('mouseleave', reset)
  return {
    destroy() {
      node.removeEventListener('mousemove', onMove)
      node.removeEventListener('mouseleave', reset)
    }
  }
}
