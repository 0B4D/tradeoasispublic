from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import yfinance as yf
from stock.stocks import get_sp500_tickers
from django.http import JsonResponse
from accounts.models import Portfolio, PortfolioItem
from decimal import Decimal, ROUND_HALF_UP
from translate.translate import translate_to_croatian
from django.core.paginator import Paginator

def stock_home(request):
    # Normal stock listing flow
    tickers, company_names = get_sp500_tickers(True)
    ticker_company_pairs = list(zip(tickers, company_names))  # Convert zip to list for pagination
   
    # Handle search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        # Filter the ticker_company_pairs based on search query
        ticker_company_pairs = [
            (ticker, company) for ticker, company in ticker_company_pairs
            if search_query.lower() in ticker.lower() or search_query.lower() in company.lower()
        ]
        # Additionally, search for stocks not registered in the app using yfinance
        try:
            ticker_data = yf.Ticker(search_query.upper().strip())
            info = ticker_data.info
            if info and "symbol" in info and info.get("shortName", "Unknown Company") != "Unknown Company":
                if info["symbol"] not in tickers:
                    ticker_company_pairs.append((info["symbol"], info.get("shortName", "Unknown Company")))
        except Exception as e:
            pass
   
    # Paginate results
    paginator = Paginator(ticker_company_pairs, 50)  # 50 stocks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    return render(request, 'stockhome.html', {'page_obj': page_obj})

@login_required
def stock_detail(request, ticker):
    try:
        # Fetch stock data from Yahoo Finance
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check if the stock data is valid
        if not info or "symbol" not in info:
            raise ValueError(f"Stock with ticker '{ticker}' not found.")
        
        name = info.get("shortName", ticker)
        pe_ratio = info.get("trailingPE")
        sector = translate_to_croatian(info.get("sector", "sektor nedostupan"))
        short_info = translate_to_croatian(info.get("longBusinessSummary", "opis nedostupan"))
        
        # Get stock price in USD
        current_price_usd = stock.history(period="1d")['Close'].iloc[-1]

        # Get exchange rate for USD to EUR
        forex = yf.Ticker("EURUSD=X")  
        exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))

        # Convert USD price to EUR
        current_price_eur = (Decimal(str(current_price_usd)) / exchange_rate).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)

        # Calculate total amount invested in the specific stock
        portfolio = Portfolio.objects.get(user=request.user)
        try:
            portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, market="F", ticker=ticker)
            total_invested = (portfolio_item.quantity * portfolio_item.purchase_price).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
            total_value = (portfolio_item.quantity * current_price_eur).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
        except PortfolioItem.DoesNotExist:
            portfolio_item = None
            total_invested = Decimal("0.0000000")
            total_value = Decimal("0.0000000")

        # Handle investment form submission
        if request.method == "POST" and current_price_eur is not None:
            investment_amount = request.POST.get('investment_amount')
            sell_amount_eur = request.POST.get('sell_amount_eur')
            sell_all = request.POST.get('sell_all')

            try:
                portfolio, _ = Portfolio.objects.get_or_create(user=request.user)

                if investment_amount:
                    investment_amount = Decimal(investment_amount).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                    if investment_amount <= 0:
                        raise ValueError("Vrijednost investicije mora biti veća od 0.")

                    # Check if the user has enough balance
                    if investment_amount > portfolio.cash_balance:
                        raise ValueError("Nedovoljno sredstava na računu.")

                    # Calculate number of shares
                    quantity = (investment_amount / current_price_eur).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)

                    # Deduct investment amount from cash balance

                    portfolio.cash_balance -= investment_amount
                    portfolio.save()

                    if portfolio_item:
                        # Calculate the weighted average purchase price
                        total_quantity = portfolio_item.quantity + quantity
                        weighted_average_price = ((portfolio_item.quantity * portfolio_item.purchase_price) + (quantity * current_price_eur)) / total_quantity

                        # Update the existing portfolio item
                        portfolio_item.quantity = total_quantity
                        portfolio_item.purchase_price = weighted_average_price.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                        portfolio_item.save()
                    else:
                        # Add new portfolio item
                        PortfolioItem.objects.create(
                            portfolio=portfolio,
                            ticker=ticker,
                            quantity=quantity,
                            purchase_price=current_price_eur,
                            market="F",  # Foreign market
                            type="stock",  # Add asset type
                        )

                elif sell_amount_eur:
                    sell_amount_eur = Decimal(sell_amount_eur).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                    if sell_amount_eur <= 0:
                        raise ValueError("Prodaja mora biti veća od 0.")

                    # Find the portfolio item
                    try:
                        portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, market="F", ticker=ticker)
                    except:
                        raise ValueError("Ne posjedujete ovu dionicu.")

                    # Calculate the number of shares to sell
                    sell_quantity = (sell_amount_eur / current_price_eur).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)

                    # Check if the user has enough shares to sell
                    if sell_quantity > portfolio_item.quantity:
                        raise ValueError("Nemate dovoljno dionica za prodaju.")

                    # Calculate the amount to be credited to cash balance
                    sell_value = (sell_quantity * current_price_eur).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)

                    # Update portfolio item quantity
                    portfolio_item.quantity -= sell_quantity
                    if portfolio_item.quantity == 0:
                        portfolio_item.delete()
                    else:
                        portfolio_item.save()

                    # Credit the sell value to cash balance
                    portfolio.cash_balance += sell_value
                    portfolio.save()

                elif sell_all:
                    # Find the portfolio item
                    portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, market="F", ticker=ticker)
                    if portfolio_item:
                        # Calculate the amount to be credited to cash balance
                        sell_value = (portfolio_item.quantity * current_price_eur).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)

                        # Delete the portfolio item
                        portfolio_item.delete()

                        # Credit the sell value to cash balance
                        portfolio.cash_balance += sell_value
                        portfolio.save()
                    else:
                        raise ValueError("Ne posjedujete ovu dionicu.")     

                return redirect('stock_detail', ticker=ticker)

            except Exception as e:
                return render(request, 'stock_detail.html', {
                    'name': name,
                    'ticker': ticker,
                    'current_price': current_price_eur,
                    'pe_ratio': pe_ratio,
                    'sector': sector,
                    'total_invested': total_invested,
                    'short_info': short_info,
                    'total_value': total_value,
                    'error_message': str(e)
                })

        return render(request, 'stock_detail.html', {
            'name': name,
            'ticker': ticker,
            'current_price': current_price_eur,
            'pe_ratio': pe_ratio,
            'sector': sector,
            'total_invested': total_invested,
            'short_info': short_info,
            'total_value': total_value
        })

    except Exception as e:
        return render(request, 'error.html', {'message': str(e)})

    
def stock_data(request, ticker):
    try:
        # Get the period from the request (default to 6mo if not provided)
        period = request.GET.get('period', '6mo')
        
        # Validate period
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y']
        if period not in valid_periods:
            period = '6mo'  # Default to 6 months if invalid
        
        interval = '1d'  # Default to daily
        if period == '1d':
            interval = '5m'
        elif period == '5d':
            interval = '15m'
        elif period == '1mo':
            interval = '1h'
        elif period in ['3mo', '6mo', '1y']:
            interval = '1d'
        elif period == '2y':
            interval = '5d'
        
        # Fetch historical stock data
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period=period, interval=interval)
        
        # Ensure data exists
        if stock_data.empty:
            return JsonResponse({'error': f"No data available for ticker '{ticker}'."}, status=404)

        # Fetch exchange rate for USD to EUR
        forex = yf.Ticker("EURUSD=X")
        exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))

        # Convert historical prices to EUR
        # Use different datetime format based on period
        if period in ['1d', '5d', '1mo']:
            # For shorter periods, include precise timestamp
            dates = stock_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        else:
            # For longer periods, just use the date
            dates = stock_data.index.strftime('%Y-%m-%d').tolist()
            
        close_prices_usd = [Decimal(str(price)) for price in stock_data['Close'].tolist()]
        close_prices_eur = [(price / exchange_rate).quantize(Decimal("0.000001")) for price in close_prices_usd]

        # Prepare and return JSON response
        chart_data = {
            'dates': dates,
            'close_prices': close_prices_eur,  # Prices now in EUR
            'period': period  # Include period in response for client-side reference
        }

        return JsonResponse(chart_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
