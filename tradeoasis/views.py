from django.shortcuts import render, redirect
import yfinance as yf
from accounts.models import Portfolio
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def testing(request):
    return render(request, 'test.html')

def home(request):
    # Fetch S&P 500 data for the last week
    sp500_tickers = ['AAPL', 'NVDA', 'MSFT', 'AMZN', 'GOOGL', 'META', 'BRK.B', 'AVGO', 'TSLA', 'WMT'] #S&P 500 tickers
    sp500_data = []

    for ticker in sp500_tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            change = ((price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            sp500_data.append({
                'ticker': ticker,
                'price': round(price, 2),
                'change': round(change, 2)
            })

    return render(request, 'home.html', {'sp500_data': sp500_data})

def stock(request):
    return render(request, 'stock.html')

def interest_calculator(request):
    return render(request, 'interest_calculator.html')

def help(request):
    return render(request, 'help.html')

def portfolio(request):
    user = request.user

    try:
        # Fetch user's portfolio
        portfolio = Portfolio.objects.get(user=user)
        portfolio_items = portfolio.items.all()  # Get all stocks in portfolio
    except Portfolio.DoesNotExist:
        # If no portfolio exists, create one with default cash balance
        portfolio = Portfolio.objects.create(user=user)
        portfolio_items = []
    
    # Initialize total portfolio value
    total_value = Decimal("0.0000000")

    # Get exchange rate for USD to EUR
    forex = yf.Ticker("EURUSD=X")
    exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))

    # Update stock prices and calculate total portfolio value
    for item in portfolio_items:
        stock = yf.Ticker(item.ticker)
        current_price_usd = stock.history(period="1d")['Close'].iloc[-1]
        current_price_eur = (Decimal(str(current_price_usd)) / exchange_rate).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)  # Convert to EUR

        # Store updated price and calculate value
        item.current_price = current_price_eur
        item.current_value = (item.quantity * current_price_eur).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
        item.profitpercentage = (item.current_price-item.purchase_price)/item.purchase_price*100
        # Add to total portfolio value
        total_value += item.current_value

    context = {
        "user": user,
        "portfolio": portfolio,
        "portfolio_items": portfolio_items,
        "total_value": total_value,
        "portfolio_value": (Decimal(portfolio.cash_balance) + total_value).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP),
    }
    
    return render(request, "yourprofile.html", context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        # Delete the user's portfolio first (assuming CASCADE doesn't handle this)
        try:
            portfolio = Portfolio.objects.get(user=user)
            # Delete all portfolio items
            portfolio.items.all().delete()
            # Delete the portfolio itself
            portfolio.delete()
        except Portfolio.DoesNotExist:
            pass  # No portfolio to delete
        
        # Delete the user account
        user.delete()
        
        # Log the user out
        logout(request)
        
        # Add a message to inform the user
        messages.success(request, "Vaš račun je uspješno izbrisan.")
        
        # Redirect to homepage or login page
        return redirect('home')  # or 'login'
    
    # If not POST method, redirect back to portfolio page
    return redirect('portfolio')

@login_required
def account_info(request):
    """
    View for displaying user account information.
    """
    user = request.user
    
    # Get portfolio information
    try:
        portfolio = Portfolio.objects.get(user=user)
        cash_balance = portfolio.cash_balance
        
        # Calculate total portfolio value
        portfolio_items = portfolio.items.all()
        total_stocks_value = Decimal("0.0000000")
        
        for item in portfolio_items:
            total_stocks_value += item.get_current_value()
            
        total_portfolio_value = (cash_balance + total_stocks_value).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    except Portfolio.DoesNotExist:
        cash_balance = Decimal("0.00")
        total_portfolio_value = Decimal("0.00")
        portfolio_items = []
    
    context = {
        'user': user,
        'cash_balance': cash_balance,
        'total_portfolio_value': total_portfolio_value,
        'num_stocks': len(portfolio_items),
    }
    
    return render(request, 'account_info.html', context)