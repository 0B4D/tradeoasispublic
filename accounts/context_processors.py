from .models import Portfolio

def user_info(request):
    return {
        'user': request.user
    }

def user_balance(request):
    """
    Context processor to make user's balance available across all templates.
    """
    context = {'user_balance': None}
    
    if request.user.is_authenticated:
        try:
            # Get the user's portfolio
            portfolio = Portfolio.objects.get(user=request.user)
            context['user_balance'] = portfolio.cash_balance
        except Portfolio.DoesNotExist:
            # If portfolio doesn't exist or model import fails, return None
            pass
            
    return context