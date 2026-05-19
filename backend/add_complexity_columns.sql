-- Add complexity columns to providers table
ALTER TABLE providers ADD COLUMN IF NOT EXISTS specializations TEXT[] DEFAULT '{}';
ALTER TABLE providers ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0;
ALTER TABLE providers ADD COLUMN IF NOT EXISTS certifications TEXT[] DEFAULT '{}';
ALTER TABLE providers ADD COLUMN IF NOT EXISTS tools_owned TEXT[] DEFAULT '{}';
ALTER TABLE providers ADD COLUMN IF NOT EXISTS can_handle_complex BOOLEAN DEFAULT false;

-- Add complexity factors to bookings (already added job_complexity in pricing migration)
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS complexity_factors JSONB;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS required_tools TEXT[] DEFAULT '{}';
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS requires_certification BOOLEAN DEFAULT false;

-- Create indexes for complexity matching
CREATE INDEX IF NOT EXISTS idx_providers_experience ON providers(experience_years);
CREATE INDEX IF NOT EXISTS idx_providers_specializations ON providers USING GIN(specializations);
CREATE INDEX IF NOT EXISTS idx_providers_can_handle_complex ON providers(can_handle_complex);
CREATE INDEX IF NOT EXISTS idx_bookings_job_complexity ON bookings(job_complexity);

-- Add check constraint for job complexity
ALTER TABLE bookings DROP CONSTRAINT IF EXISTS check_job_complexity;
ALTER TABLE bookings ADD CONSTRAINT check_job_complexity
    CHECK (job_complexity IN ('basic', 'intermediate', 'complex'));
