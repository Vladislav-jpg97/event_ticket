EVENT_TRANSITIONS = {
    "draft": {"published", "cancelled"},
    "published": {"cancelled", "completed"},
    "cancelled": set(),
    "completed": set()
}