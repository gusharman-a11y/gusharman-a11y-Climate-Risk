'use client'

import { useEffect, useRef } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Flame, Building2, Kanban, BarChart2, ArrowRight } from 'lucide-react'

const CARDS = [
  { href: '/hot-sheet',           icon: Flame,     label: 'Hot Sheet' },
  { href: '/companies',           icon: Building2,  label: 'Companies' },
  { href: '/pipeline',            icon: Kanban,     label: 'Pipeline' },
  { href: '/market-intelligence', icon: BarChart2,  label: 'Market Intel' },
]


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

      {/* Earth image — centred, sits on top of flow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-44 h-44 sm:w-56 sm:h-56 lg:w-72 lg:h-72 select-none drop-shadow-2xl">
          <Image
            src="/earth.png"
            alt="Earth"
            width={512}
            height={512}
            className="w-full h-full object-contain"
            priority
          />
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
