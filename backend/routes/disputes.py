from fastapi import APIRouter, HTTPException, Depends
from models.schemas import DisputeCreate, DisputeResolve, DisputeResponse
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from agents.dispute_resolver import dispute_resolver
from utils.notifications import create_notification
from typing import List

router = APIRouter()


@router.post("", response_model=DisputeResponse)
async def create_dispute(
    dispute: DisputeCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a dispute for a booking.
    Both users and providers can raise disputes.
    """
    try:
        # Get booking
        booking_result = supabase.table("bookings").select("*").eq("id", dispute.booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify user is part of this booking
        if current_user["role"] == "user":
            if booking["user_id"] != current_user["user_id"]:
                raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")
        else:
            # Provider - need to check provider_id
            provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
            if not provider_result.data or booking["provider_id"] != provider_result.data[0]["id"]:
                raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")

        # Check if booking is completed (disputes only after completion)
        if booking["status"] != "completed":
            raise HTTPException(status_code=400, detail="Sirf completed bookings par dispute raise ho sakti hai")

        # Check if dispute already exists
        existing_dispute = supabase.table("disputes").select("id").eq("booking_id", dispute.booking_id).execute()
        if existing_dispute.data:
            raise HTTPException(status_code=400, detail="Is booking par pehle se dispute hai")

        # Create dispute
        dispute_data = {
            "booking_id": dispute.booking_id,
            "raised_by": current_user["user_id"],
            "raised_by_role": current_user["role"],
            "dispute_type": dispute.dispute_type,
            "description": dispute.description,
            "status": "open"
        }

        result = supabase.table("disputes").insert(dispute_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Dispute create nahi hui")

        dispute_id = result.data[0]["id"]

        # Update booking
        supabase.table("bookings").update({
            "has_dispute": True,
            "dispute_status": "open"
        }).eq("id", dispute.booking_id).execute()

        # Notify other party
        other_party_id = booking["provider_id"] if current_user["role"] == "user" else booking["user_id"]

        # Get other party's user_id if they're a provider
        if current_user["role"] == "user":
            provider_result = supabase.table("providers").select("user_id").eq("id", other_party_id).execute()
            if provider_result.data:
                other_party_id = provider_result.data[0]["user_id"]

        await create_notification(
            other_party_id,
            "Dispute Raised ⚠️",
            f"A dispute has been raised for booking. Type: {dispute.dispute_type}",
            "dispute_created",
            dispute_id
        )

        # Attempt auto-resolution
        try:
            # Get provider history
            if current_user["role"] == "user":
                provider_id = booking["provider_id"]
                provider_data = supabase.table("providers").select("*, users(*)").eq("id", provider_id).execute()
                provider_history = provider_data.data[0] if provider_data.data else {}
                user_history = {}
            else:
                user_data = supabase.table("users").select("*").eq("id", booking["user_id"]).execute()
                user_history = user_data.data[0] if user_data.data else {}
                provider_history = {}

            resolution = await dispute_resolver.auto_resolve(
                dispute=result.data[0],
                booking=booking,
                provider_history=provider_history,
                user_history=user_history
            )

            # Update dispute with resolution
            if resolution["status"] in ["resolved", "escalated"]:
                supabase.table("disputes").update({
                    "status": resolution["status"],
                    "resolution": resolution["resolution"],
                    "refund_amount": resolution["refund_amount"],
                    "compensation_amount": resolution["compensation_amount"],
                    "resolved_at": "NOW()" if resolution["status"] == "resolved" else None
                }).eq("id", dispute_id).execute()

                # Notify both parties of resolution
                await create_notification(
                    current_user["user_id"],
                    "Dispute Update 📋",
                    resolution["resolution"],
                    "dispute_resolved",
                    dispute_id
                )

                await create_notification(
                    other_party_id,
                    "Dispute Update 📋",
                    resolution["resolution"],
                    "dispute_resolved",
                    dispute_id
                )

        except Exception as resolve_error:
            print(f"[DISPUTE] Auto-resolution failed: {resolve_error}")
            # Continue even if auto-resolution fails

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"[DISPUTE] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/my", response_model=List[DisputeResponse])
async def get_my_disputes(current_user: dict = Depends(get_current_user)):
    """
    Get all disputes raised by current user.
    """
    try:
        result = supabase.table("disputes").select("*").eq("raised_by", current_user["user_id"]).order("created_at", desc=True).execute()
        return result.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(
    dispute_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific dispute.
    """
    try:
        result = supabase.table("disputes").select("*").eq("id", dispute_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Dispute nahi mili")

        dispute = result.data[0]

        # Verify user is part of this dispute
        if dispute["raised_by"] != current_user["user_id"]:
            # Check if user is the other party in the booking
            booking_result = supabase.table("bookings").select("*").eq("id", dispute["booking_id"]).execute()
            if booking_result.data:
                booking = booking_result.data[0]
                if current_user["role"] == "user" and booking["user_id"] != current_user["user_id"]:
                    raise HTTPException(status_code=403, detail="Yeh dispute tumhara nahi hai")
                elif current_user["role"] == "provider":
                    provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
                    if not provider_result.data or booking["provider_id"] != provider_result.data[0]["id"]:
                        raise HTTPException(status_code=403, detail="Yeh dispute tumhara nahi hai")

        return dispute

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.put("/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: str,
    resolution: DisputeResolve,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually resolve a dispute (admin/system only).
    For now, allows the person who raised the dispute to close it.
    """
    try:
        # Get dispute
        dispute_result = supabase.table("disputes").select("*").eq("id", dispute_id).execute()
        if not dispute_result.data:
            raise HTTPException(status_code=404, detail="Dispute nahi mili")

        dispute = dispute_result.data[0]

        # For now, allow the person who raised it to close it
        if dispute["raised_by"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Sirf dispute raise karne wala close kar sakta hai")

        # Update dispute
        update_result = supabase.table("disputes").update({
            "status": "resolved",
            "resolution": resolution.resolution,
            "refund_amount": resolution.refund_amount,
            "compensation_amount": resolution.compensation_amount,
            "resolved_by": current_user["user_id"],
            "resolved_at": "NOW()"
        }).eq("id", dispute_id).execute()

        # Update booking
        supabase.table("bookings").update({
            "dispute_status": "resolved"
        }).eq("id", dispute["booking_id"]).execute()

        return {"message": "Dispute resolved successfully", "dispute": update_result.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.put("/{dispute_id}/escalate")
async def escalate_dispute(
    dispute_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Escalate a dispute to human review.
    """
    try:
        # Get dispute
        dispute_result = supabase.table("disputes").select("*").eq("id", dispute_id).execute()
        if not dispute_result.data:
            raise HTTPException(status_code=404, detail="Dispute nahi mili")

        dispute = dispute_result.data[0]

        # Verify user is part of this dispute
        if dispute["raised_by"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Yeh dispute tumhara nahi hai")

        # Update status
        update_result = supabase.table("disputes").update({
            "status": "escalated"
        }).eq("id", dispute_id).execute()

        # Notify user
        await create_notification(
            current_user["user_id"],
            "Dispute Escalated 🔺",
            "Your dispute has been escalated to our team. We'll contact you within 24 hours.",
            "dispute_escalated",
            dispute_id
        )

        return {"message": "Dispute escalated to human review", "dispute": update_result.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
