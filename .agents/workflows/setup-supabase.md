---
description: Generates complete SQL for all 7 Karoo tables with constraints, indexes, foreign keys, Realtime setup, and Pakistani seed data. Paste directly into Supabase.
---

Generate complete Supabase setup SQL for the Karoo project.

Create ALL of the following in order:

TABLE 1: users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  phone TEXT UNIQUE NOT NULL,
  email TEXT,
  password_hash TEXT NOT NULL,
  city TEXT,
  role TEXT CHECK (role IN ('user', 'provider')) DEFAULT 'user',
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

TABLE 2: providers
CREATE TABLE providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  service_type TEXT NOT NULL,
  area TEXT NOT NULL,
  lat FLOAT,
  lng FLOAT,
  rating FLOAT DEFAULT 0,
  total_reviews INTEGER DEFAULT 0,
  rate_per_hour INTEGER,
  is_available BOOLEAN DEFAULT true,
  is_online BOOLEAN DEFAULT false,
  bio TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

TABLE 3: bookings
CREATE TABLE bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  provider_id UUID REFERENCES providers(id) ON DELETE CASCADE,
  service_type TEXT NOT NULL,
  location TEXT NOT NULL,
  scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT CHECK (status IN ('pending','confirmed','completed','cancelled')) DEFAULT 'pending',
  booked_via TEXT CHECK (booked_via IN ('ai_chat','browse','request')) NOT NULL,
  note TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

TABLE 4: service_requests
CREATE TABLE service_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  service_type TEXT NOT NULL,
  location TEXT NOT NULL,
  scheduled_at TIMESTAMP WITH TIME ZONE,
  budget INTEGER,
  description TEXT,
  status TEXT CHECK (status IN ('open','taken','cancelled')) DEFAULT 'open',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

TABLE 5: messages
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role TEXT CHECK (role IN ('user', 'bot')) NOT NULL,
  content TEXT NOT NULL,
  parsed_intent JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

TABLE 6: notifications
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  type TEXT NOT NULL,
  ref_id UUID,
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

TABLE 7: reviews
CREATE TABLE reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  provider_id UUID REFERENCES providers(id) ON DELETE CASCADE,
  rating INTEGER CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

INDEXES FOR PERFORMANCE:
CREATE INDEX idx_providers_service_area ON providers(service_type, area);
CREATE INDEX idx_bookings_user ON bookings(user_id);
CREATE INDEX idx_bookings_provider ON bookings(provider_id);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX idx_service_requests_status ON service_requests(status, service_type);

REALTIME SETUP:
Enable realtime on these tables:
ALTER TABLE bookings REPLICA IDENTITY FULL;
ALTER TABLE notifications REPLICA IDENTITY FULL;
ALTER TABLE service_requests REPLICA IDENTITY FULL;

-- In Supabase dashboard enable realtime for: bookings, notifications, service_requests

SEED DATA (for testing):
Insert 5 sample providers with different service types and areas.
Insert 2 sample users.
Use realistic Pakistani names and Islamabad/Karachi area names.

After generating SQL:
1. Show complete SQL to copy into Supabase SQL editor
2. Show how to enable Realtime in Supabase dashboard (step by step)
3. Show Python code to test connection from backend
4. List all table names and row counts after seeding