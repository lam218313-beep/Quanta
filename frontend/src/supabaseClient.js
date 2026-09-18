import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://nuuqkwdopdsgokiziyum.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51dXFrd2RvcGRzZ29raXppeXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5MDYwNTgsImV4cCI6MjEwMDQ4MjA1OH0.kuGd10dtw0mfAkB05LNV7ybkyZO5Q_q99wIkJBrn5Ic'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

