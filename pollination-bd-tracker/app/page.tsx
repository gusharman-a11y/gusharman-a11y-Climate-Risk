import Link from 'next/link'
import { Flame, Building2, Kanban, BarChart2, ArrowRight } from 'lucide-react'

const CARDS = [
  { href: '/hot-sheet',           icon: Flame,    label: 'Hot Sheet' },
  { href: '/companies',           icon: Building2, label: 'Companies' },
  { href: '/pipeline',            icon: Kanban,    label: 'Pipeline' },
  { href: '/market-intelligence', icon: BarChart2, label: 'Market Intel' },
]

function EarthSVG() {
  return (
    <svg
      viewBox="0 0 500 500"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full drop-shadow-2xl"
    >
      <defs>
        {/* Ocean base gradient */}
        <radialGradient id="ocean" cx="38%" cy="35%" r="65%">
          <stop offset="0%"   stopColor="#1a6b8a" />
          <stop offset="40%"  stopColor="#0e4d6b" />
          <stop offset="100%" stopColor="#071e36" />
        </radialGradient>
        {/* Atmosphere glow */}
        <radialGradient id="atmos" cx="50%" cy="50%" r="50%">
          <stop offset="82%"  stopColor="transparent" />
          <stop offset="92%"  stopColor="#499BA6" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#499BA6" stopOpacity="0" />
        </radialGradient>
        {/* Specular highlight */}
        <radialGradient id="shine" cx="33%" cy="28%" r="40%">
          <stop offset="0%"   stopColor="#ffffff" stopOpacity="0.18" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
        {/* Dark edge vignette */}
        <radialGradient id="vignette" cx="50%" cy="50%" r="50%">
          <stop offset="70%"  stopColor="transparent" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.55" />
        </radialGradient>
        <clipPath id="globe">
          <circle cx="250" cy="250" r="230" />
        </clipPath>
      </defs>

      {/* Atmosphere glow ring outside */}
      <circle cx="250" cy="250" r="240" fill="none" stroke="#499BA6" strokeWidth="18" opacity="0.12" />
      <circle cx="250" cy="250" r="245" fill="none" stroke="#499BA6" strokeWidth="6"  opacity="0.07" />

      {/* Ocean sphere */}
      <circle cx="250" cy="250" r="230" fill="url(#ocean)" />

      {/* ─── Landmasses (clipped to globe) ─── */}
      <g clipPath="url(#globe)">

        {/* Antarctica */}
        <ellipse cx="250" cy="450" rx="160" ry="45" fill="#e8ede8" opacity="0.9" />
        <ellipse cx="180" cy="460" rx="60"  ry="28" fill="#dce8dc" opacity="0.8" />
        <ellipse cx="330" cy="455" rx="55"  ry="22" fill="#dce8dc" opacity="0.8" />

        {/* Australia — hero landmass, centred prominently */}
        <path
          d="M 290 260
             C 300 248 320 242 338 245
             C 355 248 368 258 372 272
             C 376 286 370 300 358 310
             C 348 318 335 322 320 322
             L 316 335
             C 314 342 308 346 302 344
             C 296 342 294 335 298 329
             L 296 325
             C 280 320 268 308 264 293
             C 260 278 270 264 290 260 Z"
          fill="#3a7a45"
          opacity="0.88"
        />
        {/* Tasmania */}
        <ellipse cx="330" cy="340" rx="9" ry="7" fill="#3a7a45" opacity="0.8" />
        {/* NZ */}
        <path d="M 390 265 C 393 258 400 256 404 260 C 407 264 405 272 400 276 C 395 279 388 277 387 271 Z" fill="#3a7a45" opacity="0.75" />
        <path d="M 393 280 C 396 274 404 272 408 278 C 411 284 406 292 400 294 C 394 296 389 290 390 284 Z" fill="#3a7a45" opacity="0.75" />

        {/* SE Asia archipelago */}
        <ellipse cx="310" cy="210" rx="22" ry="10" fill="#3d7d48" opacity="0.8" transform="rotate(-15 310 210)" />
        <ellipse cx="340" cy="218" rx="16" ry="8"  fill="#3d7d48" opacity="0.75" transform="rotate(-10 340 218)" />
        <ellipse cx="278" cy="205" rx="12" ry="7"  fill="#3d7d48" opacity="0.72" />
        <ellipse cx="260" cy="215" rx="10" ry="6"  fill="#3d7d48" opacity="0.7" />

        {/* Asia continent */}
        <path
          d="M 130 80 C 165 65 230 60 285 75
             C 320 85 350 100 365 120
             C 375 135 370 155 355 165
             C 338 176 310 178 290 172
             C 268 165 248 150 232 155
             C 215 160 205 178 190 185
             C 172 192 150 188 135 176
             C 115 162 105 140 108 118
             C 110 100 118 85 130 80 Z"
          fill="#4a8550"
          opacity="0.82"
        />
        {/* Indian subcontinent */}
        <path
          d="M 230 170 C 242 165 258 168 268 178
             C 278 188 278 205 268 218
             C 258 230 240 234 228 226
             C 215 218 212 200 218 186
             C 221 178 226 172 230 170 Z"
          fill="#4a8550"
          opacity="0.78"
        />
        {/* Middle East / Arabian */}
        <ellipse cx="178" cy="170" rx="30" ry="22" fill="#c8aa6a" opacity="0.72" transform="rotate(10 178 170)" />

        {/* Africa */}
        <path
          d="M 115 185 C 130 175 155 172 170 178
             C 185 184 190 198 188 215
             C 186 232 175 248 162 265
             C 150 280 138 295 130 310
             C 122 323 118 335 122 345
             C 110 340 100 325 98 308
             C 95 288 100 265 106 245
             C 110 225 108 205 115 185 Z"
          fill="#5a8f50"
          opacity="0.82"
        />

        {/* Europe */}
        <path
          d="M 100 90 C 115 78 138 72 155 76
             C 168 80 174 92 170 104
             C 166 115 152 122 138 124
             C 124 126 108 120 100 108
             C 94 98 96 92 100 90 Z"
          fill="#4a8550"
          opacity="0.8"
        />

        {/* Greenland */}
        <ellipse cx="60" cy="70" rx="32" ry="22" fill="#d8e8d8" opacity="0.75" transform="rotate(-12 60 70)" />

        {/* North America */}
        <path
          d="M 18 100 C 30 78 55 62 78 65
             C 96 68 108 82 108 100
             C 108 118 95 132 78 140
             C 62 148 42 148 28 138
             C 14 128 8 112 18 100 Z"
          fill="#4d8852"
          opacity="0.8"
        />
        {/* Central America nub */}
        <path d="M 52 145 C 56 140 64 140 68 146 C 70 152 66 160 60 162 C 54 162 50 155 52 145 Z" fill="#4d8852" opacity="0.72" />

        {/* South America */}
        <path
          d="M 48 175 C 62 162 82 158 96 164
             C 110 170 116 186 112 205
             C 108 224 94 240 78 255
             C 62 268 44 274 34 265
             C 22 255 18 235 22 215
             C 26 195 34 178 48 175 Z"
          fill="#4d8852"
          opacity="0.8"
        />

        {/* Cloud wisps */}
        <ellipse cx="200" cy="130" rx="55" ry="12" fill="white" opacity="0.18" transform="rotate(-8 200 130)" />
        <ellipse cx="310" cy="155" rx="40" ry="9"  fill="white" opacity="0.15" transform="rotate(5 310 155)" />
        <ellipse cx="140" cy="240" rx="48" ry="10" fill="white" opacity="0.14" transform="rotate(-12 140 240)" />
        <ellipse cx="360" cy="310" rx="36" ry="8"  fill="white" opacity="0.13" transform="rotate(8 360 310)" />
        <ellipse cx="230" cy="370" rx="42" ry="9"  fill="white" opacity="0.13" transform="rotate(-5 230 370)" />
        <ellipse cx="80"  cy="160" rx="32" ry="7"  fill="white" opacity="0.12" />
        <ellipse cx="400" cy="200" rx="28" ry="7"  fill="white" opacity="0.12" />

        {/* Shine highlight */}
        <circle cx="250" cy="250" r="230" fill="url(#shine)" />
        {/* Vignette dark edge */}
        <circle cx="250" cy="250" r="230" fill="url(#vignette)" />
      </g>

      {/* Outer atmosphere */}
      <circle cx="250" cy="250" r="230" fill="url(#atmos)" />
    </svg>
  )
}

export default function HomePage() {
  return (
    <div className="relative min-h-screen bg-[#040d1a] flex flex-col overflow-hidden">

      {/* Star field */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden>
        {[
          [8,12],[15,72],[22,38],[28,88],[35,15],[42,55],[48,28],[55,80],[62,44],[68,8],
          [74,66],[80,32],[86,92],[92,50],[5,60],[18,20],[32,78],[45,10],[58,50],[72,85],
          [85,18],[95,70],[12,46],[38,96],[65,62],[78,24],[90,38],[25,54],[50,70],[70,4],
        ].map(([top, left], i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white"
            style={{
              top: `${top}%`, left: `${left}%`,
              width: i % 5 === 0 ? 2 : 1,
              height: i % 5 === 0 ? 2 : 1,
              opacity: 0.3 + (i % 4) * 0.15,
            }}
          />
        ))}
      </div>

      {/* Pollination badge — top left */}
      <div className="relative z-10 p-6">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-[#499BA6]/30 flex items-center justify-center">
            <div className="w-2.5 h-2.5 rounded-full bg-[#B1DEE5]" />
          </div>
          <span className="text-[#B1DEE5] text-xs font-semibold tracking-widest uppercase">Pollination</span>
        </div>
      </div>

      {/* Main content — centred */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 -mt-8">

        {/* Earth */}
        <div className="w-64 h-64 sm:w-80 sm:h-80 lg:w-96 lg:h-96 mb-10 select-none">
          <EarthSVG />
        </div>

        {/* Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white text-center leading-tight mb-10 tracking-tight">
          Explore the Data
        </h1>

        {/* Nav cards */}
        <div className="flex flex-wrap items-center justify-center gap-3">
          {CARDS.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className="group flex items-center gap-2 bg-white/8 hover:bg-white/15 border border-white/15 hover:border-[#499BA6]/60 text-white/80 hover:text-white rounded-xl px-5 py-3 text-sm font-medium transition-all backdrop-blur-sm"
            >
              <Icon size={15} className="text-[#499BA6] group-hover:text-[#B1DEE5] transition-colors" />
              {label}
              <ArrowRight size={12} className="opacity-0 group-hover:opacity-100 -ml-0.5 transition-opacity" />
            </Link>
          ))}
        </div>
      </div>

      {/* Subtle bottom fade */}
      <div className="absolute bottom-0 inset-x-0 h-32 bg-gradient-to-t from-[#040d1a] to-transparent pointer-events-none" />
    </div>
  )
}
