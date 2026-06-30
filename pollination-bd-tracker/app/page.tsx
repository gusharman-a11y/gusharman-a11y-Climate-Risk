'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { Flame, Building2, Kanban, BarChart2, ArrowRight } from 'lucide-react'

const CARDS = [
  { href: '/hot-sheet',           icon: Flame,     label: 'Hot Sheet' },
  { href: '/companies',           icon: Building2,  label: 'Companies' },
  { href: '/pipeline',            icon: Kanban,     label: 'Pipeline' },
  { href: '/market-intelligence', icon: BarChart2,  label: 'Market Intel' },
]

function PollinationMark() {
  return (
    <svg viewBox="0 0 140 140" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
      <defs>
        {/* Main chrome vertical gradient */}
        <linearGradient id="g-chrome" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%"   stopColor="#f2f2f2" />
          <stop offset="12%"  stopColor="#c4c4c4" />
          <stop offset="28%"  stopColor="#e0e0e0" />
          <stop offset="45%"  stopColor="#a8a8a8" />
          <stop offset="60%"  stopColor="#d4d4d4" />
          <stop offset="78%"  stopColor="#b0b0b0" />
          <stop offset="100%" stopColor="#888888" />
        </linearGradient>
        {/* Horizontal sheen */}
        <linearGradient id="g-sheen" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stopColor="#fff" stopOpacity="0" />
          <stop offset="25%"  stopColor="#fff" stopOpacity="0.22" />
          <stop offset="50%"  stopColor="#fff" stopOpacity="0.06" />
          <stop offset="75%"  stopColor="#fff" stopOpacity="0.18" />
          <stop offset="100%" stopColor="#000" stopOpacity="0.08" />
        </linearGradient>
        {/* Inner circle */}
        <radialGradient id="g-dot" cx="38%" cy="32%" r="65%">
          <stop offset="0%"   stopColor="#ebebeb" />
          <stop offset="45%"  stopColor="#b8b8b8" />
          <stop offset="100%" stopColor="#707070" />
        </radialGradient>
        <filter id="f-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="6" stdDeviation="10" floodColor="#000" floodOpacity="0.22" />
        </filter>
        <filter id="f-inner">
          <feDropShadow dx="0" dy="-2" stdDeviation="3" floodColor="#000" floodOpacity="0.15" />
        </filter>
      </defs>

      {/* Shadow layer */}
      <rect x="14" y="14" width="112" height="112" rx="26" ry="26"
            fill="#b0b0b0" opacity="0.4" transform="translate(0,8)" />

      {/* Main rounded square */}
      <rect x="14" y="14" width="112" height="112" rx="26" ry="26"
            fill="url(#g-chrome)" filter="url(#f-shadow)" />

      {/* Horizontal sheen overlay */}
      <rect x="14" y="14" width="112" height="112" rx="26" ry="26"
            fill="url(#g-sheen)" />

      {/* Top edge highlight */}
      <rect x="14" y="14" width="112" height="3" rx="2"
            fill="#ffffff" opacity="0.5" />
      <rect x="14" y="14" width="3" height="112" rx="2"
            fill="#ffffff" opacity="0.2" />

      {/* Inner dot */}
      <circle cx="70" cy="70" r="22"
              fill="url(#g-dot)" filter="url(#f-inner)" />

      {/* Dot highlight */}
      <circle cx="63" cy="62" r="7"
              fill="#ffffff" opacity="0.28" />
    </svg>
  )
}

export default function HomePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let W = 0, H = 0

    type P = { x: number; baseY: number; speed: number; r: number; a: number; phase: number }
    let particles: P[] = []

    const init = () => {
      W = canvas.offsetWidth
      H = canvas.offsetHeight
      canvas.width = W
      canvas.height = H
      particles = []
      for (let i = 0; i < 6000; i++) {
        // Concentrate particles in the central 30% band
        particles.push({
          x: Math.random() * W,
          baseY: H * 0.35 + Math.random() * H * 0.30,
          speed: 0.15 + Math.random() * 0.65,
          r: 0.3 + Math.random() * 1.2,
          a: 0.06 + Math.random() * 0.32,
          phase: Math.random() * Math.PI * 2,
        })
      }
    }
    init()
    window.addEventListener('resize', init)

    let t = 0, raf = 0

    const draw = () => {
      ctx.clearRect(0, 0, W, H)
      t += 0.4

      const midY = H * 0.5
      const band = H * 0.28  // tighter band = clearer wave shape

      for (const p of particles) {
        p.x += p.speed
        if (p.x > W + 10) { p.x = -10 }

        // Higher amplitude waves so flow is visually obvious
        const wave =
          Math.sin(t * 0.007 + p.phase         + p.x * 0.008) * 50 +
          Math.sin(t * 0.004 + p.phase * 1.6   + p.x * 0.005) * 28 +
          Math.sin(t * 0.002 + p.phase * 0.7   + p.x * 0.002) * 14

        const y = p.baseY + wave
        const dist = Math.abs(y - midY) / band
        if (dist > 1) continue

        // Sharp falloff — clear empty space above/below waves
        const falloff = Math.pow(1 - dist, 1.4)
        ctx.fillStyle = `rgba(45,45,45,${p.a * falloff})`
        ctx.beginPath()
        ctx.arc(p.x, y, p.r, 0, Math.PI * 2)
        ctx.fill()
      }

      raf = requestAnimationFrame(draw)
    }
    draw()

    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', init) }
  }, [])

  return (
    <div
      className="relative flex flex-col overflow-hidden"
      style={{ height: 'calc(100vh - 56px)', background: '#f5f4f1' }}
    >
      {/* Wordmark */}
      <div className="relative z-20 flex justify-center pt-10">
        <span
          className="text-[#1a1a1a] font-light tracking-[0.28em] uppercase select-none"
          style={{ fontSize: 15 }}
        >
          pollination
        </span>
      </div>

      {/* Particle canvas layer */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
      />

      {/* Pollination mark — centred, sits on top of flow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-36 h-36 sm:w-48 sm:h-48 lg:w-56 lg:h-56 select-none">
          <PollinationMark />
        </div>
      </div>

      {/* Bottom: headline + nav */}
      <div className="relative z-20 mt-auto flex flex-col items-center pb-12 px-6">
        <p
          className="text-[#111] text-center font-medium mb-8 leading-snug"
          style={{ fontSize: 'clamp(22px, 4vw, 42px)' }}
        >
          Explore the Data
        </p>

        <div className="flex flex-wrap items-center justify-center gap-2.5">
          {CARDS.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className="group flex items-center gap-2 bg-white/80 hover:bg-white border border-black/10 hover:border-black/25 text-[#222] rounded-full px-5 py-2 text-[13px] font-medium transition-all backdrop-blur-sm shadow-sm"
            >
              <Icon size={13} className="text-[#10545D]" />
              {label}
              <ArrowRight size={11} className="opacity-0 group-hover:opacity-50 -ml-1 transition-opacity" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
