from .access import account_role, can_manage_lists, can_manage_users

def navigation(request):
    user = request.user
    return {
        'account_role': account_role(user),
        'can_manage_lists': can_manage_lists(user),
        'can_manage_users': can_manage_users(user),
    }
