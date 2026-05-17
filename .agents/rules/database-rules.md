---
trigger: always_on
---

Always use Supabase Python client, never raw SQL strings.
Check if result.data is empty before accessing index 0.
Use service_role key in backend, anon key in frontend only.
After any booking status change, insert into notifications 
table for both user_id and provider user_id.
Always filter providers by is_available=true in queries.