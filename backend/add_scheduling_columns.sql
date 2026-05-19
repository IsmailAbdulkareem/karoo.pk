-- Add scheduling columns to bookings table
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS duration_minutes INTEGER DEFAULT 60;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS travel_time_minutes INTEGER;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS buffer_time_minutes INTEGER DEFAULT 15;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS actual_start_time TIMESTAMP;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS actual_end_time TIMESTAMP;

-- Create waitlist table
CREATE TABLE IF NOT EXISTS booking_waitlist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider_id UUID REFERENCES providers(id) ON DELETE CASCADE,
    service_type VARCHAR(100) NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time_start TIME,
    preferred_time_end TIME,
    status VARCHAR(20) DEFAULT 'waiting',
    notified_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '48 hours'),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for faster scheduling queries
CREATE INDEX IF NOT EXISTS idx_bookings_provider_scheduled ON bookings(provider_id, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_bookings_status_scheduled ON bookings(status, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_waitlist_status ON booking_waitlist(status);
CREATE INDEX IF NOT EXISTS idx_waitlist_service_type ON booking_waitlist(service_type);
CREATE INDEX IF NOT EXISTS idx_waitlist_expires ON booking_waitlist(expires_at);

-- Add check constraints (using DO block for idempotency)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'check_waitlist_status'
    ) THEN
        ALTER TABLE booking_waitlist ADD CONSTRAINT check_waitlist_status
            CHECK (status IN ('waiting', 'notified', 'expired', 'fulfilled'));
    END IF;
END $$;

-- Add trigger to auto-expire waitlist entries
CREATE OR REPLACE FUNCTION expire_old_waitlist_entries()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE booking_waitlist
    SET status = 'expired'
    WHERE status = 'waiting'
    AND expires_at < NOW();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_expire_waitlist ON booking_waitlist;
CREATE TRIGGER trigger_expire_waitlist
    AFTER INSERT OR UPDATE ON booking_waitlist
    FOR EACH STATEMENT
    EXECUTE FUNCTION expire_old_waitlist_entries();

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_waitlist_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_waitlist_updated_at ON booking_waitlist;
CREATE TRIGGER trigger_update_waitlist_updated_at
    BEFORE UPDATE ON booking_waitlist
    FOR EACH ROW
    EXECUTE FUNCTION update_waitlist_updated_at();
