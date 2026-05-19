from db.supabase_client import supabase

async def create_notification(user_id: str, title: str, body: str,
                               type: str, ref_id: str = None):
    try:
        supabase.table("notifications").insert({
            "user_id": user_id,
            "title": title,
            "body": body,
            "type": type,
            "ref_id": ref_id
        }).execute()
    except Exception as e:
        print(f"[NOTIFICATION ERROR] {e}")

async def notify_booking_created(booking_id, user_id, provider_user_id,
                                  provider_name, user_name, service_type):
    await create_notification(user_id,
        "Booking Bhej Di Gayi ✅",
        f"{provider_name} ko tumhari {service_type} request mili",
        "booking_created", booking_id)
    await create_notification(provider_user_id,
        "Naya Booking Request! 🔔",
        f"{user_name} ko {service_type} chahiye",
        "booking_created", booking_id)

async def notify_booking_accepted(booking_id, user_id, provider_user_id,
                                   provider_name, scheduled_at):
    await create_notification(user_id,
        "Booking Confirm Ho Gayi! ✅",
        f"{provider_name} aa raha hai {scheduled_at} ko",
        "booking_accepted", booking_id)
    await create_notification(provider_user_id,
        "Job Confirm",
        "Tumne booking accept kar li",
        "booking_accepted", booking_id)

async def notify_booking_rejected(booking_id, user_id, provider_user_id, provider_name):
    await create_notification(user_id,
        "Booking Reject Ho Gayi ❌",
        f"{provider_name} available nahi hai. Doosra provider choose karo.",
        "booking_rejected", booking_id)
    await create_notification(provider_user_id,
        "Booking Reject Ki",
        "Tumne yeh booking reject kar di",
        "booking_rejected", booking_id)

async def notify_booking_completed(booking_id, user_id, provider_user_id, user_name):
    await create_notification(user_id,
        "Kaam Mukammal! ⭐",
        "Please apna experience rate karo",
        "booking_completed", booking_id)
    await create_notification(provider_user_id,
        "Job Complete",
        f"{user_name} ki service complete ho gayi. Rate the customer.",
        "booking_completed", booking_id)

async def notify_booking_cancelled_by_user(booking_id, user_id, provider_user_id, user_name, service_type):
    await create_notification(user_id,
        "Booking Cancel Ho Gayi 🚫",
        f"Tumne apni {service_type} booking cancel kar di",
        "booking_cancelled", booking_id)
    await create_notification(provider_user_id,
        "Booking Cancel Ho Gayi ❌",
        f"{user_name} ne {service_type} booking cancel kar di",
        "booking_cancelled", booking_id)

async def notify_booking_cancelled_by_provider(booking_id, user_id, provider_user_id, provider_name, service_type):
    await create_notification(user_id,
        "Provider Ne Cancel Kiya ❌",
        f"{provider_name} ne tumhari {service_type} booking cancel kar di. Doosra provider choose karo.",
        "booking_cancelled", booking_id)
    await create_notification(provider_user_id,
        "Booking Cancel Ki 🚫",
        f"Tumne {service_type} booking cancel kar di",
        "booking_cancelled", booking_id)
