-- Grant permissions for service_progress table
GRANT SELECT, INSERT, UPDATE, DELETE ON public.service_progress TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.disputes TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.booking_waitlist TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversations TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversation_messages TO service_role;

-- Grant sequence permissions if needed
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Verify permissions
SELECT
    grantee,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'service_role'
  AND table_name IN ('service_progress', 'disputes', 'booking_waitlist', 'conversations', 'conversation_messages')
ORDER BY table_name, privilege_type;
