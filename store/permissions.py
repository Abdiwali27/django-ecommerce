def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name="Admin").exists()
    )


def is_staff_member(user):
    return user.is_authenticated and (
        user.groups.filter(name="Staff").exists()
    )