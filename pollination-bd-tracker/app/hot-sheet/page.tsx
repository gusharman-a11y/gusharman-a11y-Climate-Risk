import { unstable_cache } from 'next/cache'
import { getHotSheet } from '@/lib/data'
import HotSheetClient from '@/components/HotSheetClient'

export const dynamic = 'force-dynamic'

const getCachedHotSheet = unstable_cache(
  getHotSheet,
  ['hot-sheet'],
  { revalidate: 120 },
)

export default async function HotSheetPage() {
  const companies = await getCachedHotSheet()
  return <HotSheetClient companies={companies} />
}
