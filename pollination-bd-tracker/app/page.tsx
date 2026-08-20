'use client'

import { useEffect, useRef } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Flame, Building2, Kanban, BarChart2, ArrowRight } from 'lucide-react'

const CARDS = [
  { href: '/hot-sheet',           icon: Flame,     label: 'Target Clients' },
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

    type P = {
      x: number
      baseY: number
      // each particle has a drift speed (direction baked in, tide flips sign)
      speed: number
      r: number
      a: number
      phase: number
      phaseX: number  // per-particle horizontal phase offset for wave back-and-forth
    }
    let particles: P[] = []

    const init = () => {
      W = canvas.offsetWidth
      H = canvas.offsetHeight
      canvas.width = W
      canvas.height = H
      particles = []
      for (let i = 0; i < 5000; i++) {
        particles.push({
          x: Math.random() * W,
          baseY: H * 0.32 + Math.random() * H * 0.36,
          speed: 0.4 + Math.random() * 1.2,
          r: 1.2 + Math.random() * 3.2,     // bigger pixels
          a: 0.12 + Math.random() * 0.40,
          phase: Math.random() * Math.PI * 2,
          phaseX: Math.random() * Math.PI * 2,
        })
      }
    }
    init()
    window.addEventListener('resize', init)

    let t = 0, raf = 0

    const draw = () => {
      ctx.clearRect(0, 0, W, H)
      t += 0.35

      // Global tide: sin oscillates between -1 and +1 → particles flow right then left
      const tide = Math.sin(t * 0.0018)

      const midY = H * 0.5
      const band = H * 0.30

      // Globe exclusion — matches CSS clamp(280px,46vw,580px)/2, centre offset by paddingBottom:6vh
      const globeR = Math.min(W * 0.23, 290) + 4 // +4px soft buffer
      const globeCX = W * 0.5
      const globeCY = H * 0.5 - H * 0.03 // paddingBottom:6vh shifts centre up ~3% of H

      for (const p of particles) {
        // Back-and-forth: tide drives direction, phaseX gives each particle slight lag
        const dir = Math.sin(t * 0.0018 + p.phaseX * 0.3)
        p.x += p.speed * dir

        // Wrap both edges
        if (p.x > W + 60) p.x = -60
        if (p.x < -60) p.x = W + 60

        // Vertical wave — multiple frequencies for organic look
        const wave =
          Math.sin(t * 0.006 + p.phase           + p.x * 0.007) * 55 +
          Math.sin(t * 0.003 + p.phase * 1.8     + p.x * 0.004) * 30 +
          Math.sin(t * 0.0015 + p.phase * 0.6    + p.x * 0.002) * 15

        const y = p.baseY + wave

        // Skip particles inside the globe so they flow behind it
        const dx = p.x - globeCX, dy = y - globeCY
        if (dx * dx + dy * dy < globeR * globeR) continue

        const dist = Math.abs(y - midY) / band
        if (dist > 1) continue

        const falloff = Math.pow(1 - dist, 1.3)
        // Slightly darker where tide is moving fast (centre of swing)
        const speedBoost = Math.abs(tide) * 0.15
        ctx.fillStyle = `rgba(30,30,30,${(p.a + speedBoost) * falloff})`
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
      style={{ height: 'calc(100vh - 56px)', background: '#ffffff' }}
    >
      {/* Wordmark */}
      <div className="relative z-20 flex justify-center pt-8">
        <span
          className="text-[#1a1a1a] font-light tracking-[0.28em] uppercase select-none"
          style={{ fontSize: 14 }}
        >
          carbon intelligence
        </span>
      </div>

      {/* Particle canvas — fills everything */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
      />

      {/* Earth — sits above canvas; canvas skips the globe circle so particles flow behind */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ paddingBottom: '6vh' }}>
        <div
          className="select-none"
          style={{
            width: 'clamp(280px, 46vw, 580px)',
            height: 'clamp(280px, 46vw, 580px)',
            borderRadius: '50%',
            overflow: 'hidden',
          }}
        >
          <Image
            src="/earth.png"
            alt="Earth"
            width={800}
            height={800}
            className="earth-spin w-full h-full object-cover"
            priority
          />
        </div>
      </div>

      {/* Bottom: headline + nav */}
      <div className="relative z-20 mt-auto flex flex-col items-center pb-10 px-6">
        <p
          className="text-[#111] text-center font-medium mb-6 leading-tight tracking-tight"
          style={{ fontSize: 'clamp(26px, 4.5vw, 52px)' }}
        >
          Explore the Data
        </p>

        <div className="flex flex-wrap items-center justify-center gap-2.5">
          {CARDS.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className="group flex items-center gap-2 bg-white hover:bg-[#f6f7fb] border border-black/12 hover:border-black/25 text-[#222] rounded-full px-5 py-2 text-[13px] font-medium transition-all shadow-sm"
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
