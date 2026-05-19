-- Create disputes table
CREATE TABLE IF NOT EXISTS disputes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    raised_by UUID REFERENCES users(id),
    raised_by_role VARCHAR(20) NOT NULL,
    dispute_type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    resolution TEXT,
    refund_amount INTEGER DEFAULT 0,
    compensation_amount INTEGER DEFAULT 0,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add dispute columns to bookings table
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS has_dispute BOOLEAN DEFAULT false;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS dispute_status VARCHAR(20);

-- Add blacklist columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_blacklisted BOOLEAN DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS blacklist_reason TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS blacklisted_at TIMESTAMP;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_disputes_booking_id ON disputes(booking_id);
CREATE INDEX IF NOT EXISTS idx_disputes_raised_by ON disputes(raised_by);
CREATE INDEX IF NOT EXISTS idx_disputes_status ON disputes(status);
CREATE INDEX IF NOT EXISTS idx_disputes_type ON disputes(dispute_type);
CREATE INDEX IF NOT EXISTS idx_bookings_has_dispute ON bookings(has_dispute);
CREATE INDEX IF NOT EXISTS idx_users_is_blacklisted ON users(is_blacklisted);

-- Add check constraints (using DO block for idempotency)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_dispute_type') THEN
        ALTER TABLE disputes ADD CONSTRAINT check_dispute_type
            CHECK (dispute_type IN ('no_show', 'quality_issue', 'price_disagreement', 'time_overrun', 'unprofessional_behavior', 'safety_concern', 'other'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_dispute_status') THEN
        ALTER TABLE disputes ADD CONSTRAINT check_dispute_status
            CHECK (status IN ('open', 'investigating', 'resolved', 'escalated', 'closed'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_raised_by_role') THEN
        ALTER TABLE disputes ADD CONSTRAINT check_raised_by_role
            CHECK (raised_by_role IN ('user', 'provider'));
    END IF;
END $$;

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_disputes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_disputes_updated_at ON disputes;
CREATE TRIGGER trigger_update_disputes_updated_at
    BEFORE UPDATE ON disputes
    FOR EACH ROW
    EXECUTE FUNCTION update_disputes_updated_at();
