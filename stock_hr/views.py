from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_UP
from accounts.models import Portfolio, PortfolioItem
import os

ZSE_XML_URL = os.environ.get('ZSE_XML_URL')

def fetch_stocks():
    response = requests.get(ZSE_XML_URL)
    
    if response.status_code != 200:
        return []  # Return empty list if the request fails
    
    root = ET.fromstring(response.text)
    
    stocks = []
    for stock in root.findall(".//secboardData/secboard"):
        name = stock.get("secCode")
        bid_price = stock.find("bidPrice").text or "N/A"
        offer_price = stock.find("offerPrice").text or "N/A"
        last_price = stock.find("lastPrice").text or "N/A"
        change_percent = stock.find("changePercent").text or "0"

        stocks.append({
            "name": name,
            "bid_price": bid_price,
            "offer_price": offer_price,
            "last_price": last_price,
            "change_percent": float(change_percent) if change_percent != "N/A" else 0
        })
    
    return stocks

def stock_home_hr(request):
    stocks = fetch_stocks()  # Fetch stock data
    return render(request, "stock_home_hr.html", {"stocks": stocks})

def fetch_index_detail(index_name):
    """Fetch index details from XML by ticker"""
    response = requests.get(ZSE_XML_URL)

    if response.status_code != 200:
        return None  # If request fails, return None

    root = ET.fromstring(response.text)

    # Search for indexes
    for index in root.findall(".//indexData/index"):
        name = index.get("secCode")
        if name == index_name:
            value = index.find("value").text if index.find("value") is not None else None
            price = Decimal(value) if value else None
            change = index.find("changePercent").text
            if change is None:
                change = 0.00
            else:
                change = float(change)
            return {
                "name": name,
                "price": price,
                "change": change,
                "type": "index"
            }

def fetch_stock_detail(stock_name):
    """Fetch stock details from XML by ticker"""
    response = requests.get(ZSE_XML_URL)

    if response.status_code != 200:
        return None  # If request fails, return None

    root = ET.fromstring(response.text)

    # Search for stocks
    for stock in root.findall(".//secboardData/secboard"):
        name = stock.get("secCode")
        if name == stock_name:
            last_price = stock.find("lastPrice").text if stock.find("lastPrice") is not None else None
            offer_price = stock.find("offerPrice").text if stock.find("offerPrice") is not None else None
            bid_price = stock.find("bidPrice").text if stock.find("bidPrice") is not None else None
        
            price = last_price or offer_price or bid_price
            price = Decimal(price) if price else None
            change = stock.find("changePercent").text
            if change is None:
                change = 0.00
            else:
                change = float(change)
            return {
                "name": name,
                "price": price,
                "change": change,
                "type": "stock"
            }

    return None  # Return None if asset is not found

@login_required
def asset_detail_hr(request, asset_name, asset_type):
    if asset_type == "index":
        asset = fetch_index_detail(asset_name)
    elif asset_type == "stock":
        asset = fetch_stock_detail(asset_name)
    if not asset:
        return render(request, "error.html", {"asset_name": asset_name})  # Handle 404

    user = request.user
    portfolio, _ = Portfolio.objects.get_or_create(user=user)
    message = ''

    try:
        portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, market="HR", ticker=asset_name)
        total_invested = (portfolio_item.quantity * portfolio_item.purchase_price).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
        total_value = (portfolio_item.quantity * asset["price"]).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP) if asset["price"] else Decimal("0.00")
    except PortfolioItem.DoesNotExist:
        portfolio_item = None
        total_invested = Decimal("0.0000000")
        total_value = Decimal("0.0000000")

    if request.method == "POST" and asset["price"] is not None:
        investment_quantity = request.POST.get("investment_quantity")
        sell_quantity = request.POST.get("sell_quantity")
        sell_all = request.POST.get("sell_all") == "true"  # Convert to boolean

        try:
            portfolio, _ = Portfolio.objects.get_or_create(user=request.user)

            if investment_quantity:

                investment_quantity = Decimal(investment_quantity).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                investment_amount = (investment_quantity * asset["price"]).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                if investment_amount <= 0:
                    raise ValueError("Vrijednost investicije mora biti veća od 0.")
                
                # Check if the user has enough cash balance
                if investment_amount > portfolio.cash_balance:
                    raise ValueError("Nedovoljno sredstava na računu.")
                
                portfolio.cash_balance -= investment_amount
                portfolio.save()

                if portfolio_item:
                    total_quantity = portfolio_item.quantity + investment_quantity
                    weighted_average_price = ((portfolio_item.purchase_price * portfolio_item.quantity) + investment_amount) / total_quantity

                    portfolio_item.quantity = total_quantity
                    portfolio_item.purchase_price = weighted_average_price.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                    portfolio_item.save()
                    message = f"Uspješno ste investirali {investment_quantity} dionica {asset_name} po cijeni {asset['price']}."
                else:
                    # Add new portfolio item
                    PortfolioItem.objects.create(
                        portfolio=portfolio,
                        ticker=asset_name,
                        quantity=investment_quantity,
                        purchase_price=asset["price"],
                        market="HR",
                        type=asset["type"]
                    )
                    message = f"Uspješno ste investirali {investment_quantity} dionica {asset_name} po cijeni {asset['price']}."

            elif sell_quantity:
                sell_quantity = Decimal(sell_quantity).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                sell_amount = (sell_quantity * asset["price"]).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                if sell_amount <= 0:
                    raise ValueError("Prodaja mora biti veća od 0.")
                
                # Find the portfolio item
                try:
                    portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, market="HR", ticker=asset_name)
                except PortfolioItem.DoesNotExist:
                    raise ValueError("Ne posjedujete ovu dionicu.")
                
                # Check if the user has enough shares to sell
                if sell_quantity > portfolio_item.quantity:
                    raise ValueError("Nemate dovoljno dionica za prodaju.")
                
                sell_value = (sell_quantity * asset["price"]).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                portfolio_item.quantity -= sell_quantity
                if portfolio_item.quantity == 0:
                    portfolio_item.delete()
                else:
                    portfolio_item.save()

                portfolio.cash_balance += sell_value
                portfolio.save()
                message = f"Uspješno ste prodali {sell_quantity} dionica {asset_name}."

            elif sell_all:
                # Find the portfolio item
                try:
                    portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, market="HR", ticker=asset_name)
                except PortfolioItem.DoesNotExist:
                    raise ValueError("Ne posjedujete ovu dionicu.")
                
                sell_value = (portfolio_item.quantity * asset["price"]).quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
                portfolio.cash_balance += sell_value
                portfolio_item.delete()
                portfolio.save()
                message = f"Uspješno ste prodali sve dionice {asset_name}."
            
            return redirect("stock_hr:asset_detail_hr", asset_name=asset_name, asset_type=asset_type)

        except Exception as e:
            return render(request, "stock_detail_hr.html", {
                "asset": asset,
                "portfolio_item": portfolio_item,
                "total_invested": total_invested,
                "total_value": total_value,
                "error_message": str(e),
            })

    return render(request, "stock_detail_hr.html", {
        "asset": asset,
        "portfolio_item": portfolio_item,
        "total_invested": total_invested,
        "total_value": total_value,
        "message": message,
    })

def fetch_indexes():
    response = requests.get(ZSE_XML_URL)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.content)
    indexes = []

    for index in root.findall(".//index"):
        sec_code = index.get("secCode")
        value = index.find("value").text
        change_percent = index.find("changePercent").text

        indexes.append({
            "name": sec_code,
            "value": float(value),
            "change": float(change_percent)
        })

    return indexes

def indexes(request):
    indexes = fetch_indexes()
    return render(request, "indexes.html", {"indexes": indexes})

