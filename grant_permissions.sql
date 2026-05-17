-- Grant all permissions to service_role for all tables


GRANT ALL ON public.users TO service_role;
GRANT ALL ON public.providers TO service_role;
GRANT ALL ON public.bookings TO service_role;
GRANT ALL ON public.ratings TO service_role;
GRANT ALL ON public.notifications TO service_role;
GRANT ALL ON public.service_requests TO service_role;
GRANT ALL ON public.messages TO service_role;

-- Grant usage on sequences (for auto-increment IDs if any)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Also grant to anon role for public access (if needed)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.providers TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.bookings TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.ratings TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.notifications TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.service_requests TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.messages TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;
