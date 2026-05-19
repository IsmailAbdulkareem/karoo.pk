-- Add pricing columns to bookings table
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS base_price INTEGER;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS distance_fee INTEGER;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS urgency_fee INTEGER;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS complexity_fee INTEGER;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS surge_multiplier FLOAT DEFAULT 1.0;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS loyalty_discount INTEGER DEFAULT 0;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS final_price INTEGER;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS price_breakdown JSONB;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS urgency VARCHAR(20) DEFAULT 'normal';
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS job_complexity VARCHAR(20) DEFAULT 'basic';

-- Add pricing columns to providers table
ALTER TABLE providers ADD COLUMN IF NOT EXISTS base_rate INTEGER DEFAULT 500;
ALTER TABLE providers ADD COLUMN IF NOT EXISTS surge_enabled BOOLEAN DEFAULT true;

-- Add loyalty level to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS loyalty_level INTEGER DEFAULT 0;

-- Create index for faster price queries
CREATE INDEX IF NOT EXISTS idx_bookings_final_price ON bookings(final_price);
CREATE INDEX IF NOT EXISTS idx_bookings_urgency ON bookings(urgency);
CREATE INDEX IF NOT EXISTS idx_bookings_complexity ON bookings(job_complexity);
