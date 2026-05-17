---
description: Adds notification logic for any booking event. Creates records for both user and provider sides with correct titles and Supabase Realtime push setup.
---

Add notification logic to the Karoo backend for a specific event.

Ask me:
1. What event is triggering the notification? 
   (booking created, booking accepted, booking rejected, booking completed, 
   request posted, provider applied to request, review received)
2. Which file and endpoint should trigger this?

Based on the event, generate notification records for BOTH sides using this map:

NOTIFICATION MAP:

Event: booking_created
  User notification:    title="Booking Sent", body="Tumhari booking {provider_name} ko bhej di gayi"
  Provider notification: title="New Booking Request!", body="{user_name} ne {service_type} book kiya hai {location} mein"

Event: booking_accepted  
  User notification:    title="Booking Confirmed!", body="{provider_name} aa raha hai {scheduled_at} ko"
  Provider notification: title="Job Confirmed", body="Tumne {user_name} ki booking accept kar li"

Event: booking_rejected
  User notification:    title="Booking Rejected", body="{provider_name} available nahi hai. Doosra provider choose karo"
  Provider notification: title="Booking Rejected", body="Tumne {user_name} ki request reject kar di"

Event: booking_completed
  User notification:    title="Service Complete!", body="Please rate your experience with {provider_name}"
  Provider notification: title="Job Complete", body="{user_name} ki service complete ho gayi"

Event: request_posted
  Provider notification: title="New Job Near You!", body="{service_type} ki zaroorat hai {location} mein"

Event: provider_applied
  User notification:    title="Provider Interested!", body="{provider_name} tumhari request pe apply kiya"

NOTIFICATION HELPER FUNCTION:
Create backend/utils/notifications.py with:

async def create_notification(user_id: str, title: str, body: str, type: str, ref_id: str = None):
    try:
        supabase.table("notifications").insert({
            "user_id": user_id,
            "title": title,
            "body": body,
            "type": type,
            "ref_id": ref_id
        }).execute()
    except Exception as e:
        print(f"Notification error: {e}")

async def notify_both(user_id: str, provider_user_id: str, event: str, data: dict):
    # Creates notifications for both user and provider based on event type
    pass

After generating:
1. Show complete notifications.py utility file
2. Show exactly where to call notify_both() in the endpoint
3. Show how Supabase Realtime will push this to frontend
4. Show frontend code (realtime.ts) to subscribe and display notification
5. Show how to update unread count badge on bell icon