def violates_permission(permission, forbidden):
    """
    Check whether Windows ACL rights violate a policy.

    Improvement:
    FullControl includes Modify, so FullControl must also
    be detected when the policy forbids Modify.
    """
    rights = {
        item.strip().casefold()
        for item in permission.split(",")
    }

    forbidden = forbidden.strip().casefold()

    if forbidden == "modify":
        return "modify" in rights or "fullcontrol" in rights

    return forbidden in rights
