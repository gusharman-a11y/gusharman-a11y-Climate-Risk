import { createClient } from '@supabase/supabase-js'

// Carbon-intel Supabase — ACCU / Safeguard / OffsetsDB data (read-only anon)
export const sbCarbon = createClient(
  'https://eayyzukfcvyvcsgnnfby.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVheXl6dWtmY3Z5dmNzZ25uZmJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIzNjUxMzIsImV4cCI6MjA5Nzk0MTEzMn0.UNuaIEHqomzSPQCMjE2LlFrjjUz22JFzUgww_hW2RzU'
)
