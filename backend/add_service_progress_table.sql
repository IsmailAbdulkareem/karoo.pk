-- Create service_progress table for real-time status tracking
CREATE TABLE IF NOT EXISTS service_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    location_lat FLOAT,
    location_lng FLOAT,
    notes TEXT,
    photo_urls TEXT[] DEFAULT '{}',
    checklist_items JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add current status to bookings table
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS current_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS status_updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS completion_checklist JSONB;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS checklist_completed BOOLEAN DEFAULT false;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_service_progress_booking ON service_progress(booking_id);
CREATE INDEX IF NOT EXISTS idx_service_progress_status ON service_progress(status);
CREATE INDEX IF NOT EXISTS idx_service_progress_created_at ON service_progress(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bookings_current_status ON bookings(current_status);

-- Add check constraint for service progress status (using DO block for idempotency)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_progress_status') THEN
        ALTER TABLE service_progress ADD CONSTRAINT check_progress_status
            CHECK (status IN ('en_route', 'arrived', 'in_progress', 'paused', 'completed', 'issue_reported'));
    END IF;
END $$;

-- Add check constraint for booking current status
ALTER TABLE bookings DROP CONSTRAINT IF EXISTS check_current_status;
ALTER TABLE bookings ADD CONSTRAINT check_current_status
    CHECK (current_status IN ('pending', 'confirmed', 'en_route', 'arrived', 'in_progress', 'paused', 'completed', 'cancelled'));

-- Add trigger to update status_updated_at
CREATE OR REPLACE FUNCTION update_booking_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_status IS DISTINCT FROM OLD.current_status THEN
        NEW.status_updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_booking_status_timestamp ON bookings;
CREATE TRIGGER trigger_update_booking_status_timestamp
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_booking_status_timestamp();
