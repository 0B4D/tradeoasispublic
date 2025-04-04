from django.contrib.auth.models import AbstractUser
from django.db import models
import yfinance as yf
from decimal import Decimal
import requests
import xml.etree.ElementTree as ET
import os

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.username

class Portfolio(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=8, default=10000.00)  # Default $10,000 starting balance

    def get_total_value(self):
        total_value = self.cash_balance  # Start with cash balance
        portfolio_items = self.items.all()  # Get all portfolio items using the related name "items"

        for item in portfolio_items:
            total_value += item.get_current_value()

        return total_value

class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="items")
    ticker = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=15, decimal_places=9)  # Increased precision for fractional shares
    purchase_price = models.DecimalField(max_digits=15, decimal_places=7)  # Ensure price is stored accurately
    market = models.CharField(max_length=10, default="F")  # Default to F (foreign)
    type = models.CharField(max_length=10, default="stock")  # Default to stock
    
    def get_current_price(self):
        if self.market == "F":
            return self.get_foreign_price()
        elif self.market == "HR":
            return self.get_hr_price()
        else:
            return None
    
    def get_foreign_price(self):
        """Fetch the latest stock price using yfinance"""
        stock = yf.Ticker(self.ticker)
        forex = yf.Ticker("EURUSD=X")
        exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))
        current_price = Decimal(str(stock.history(period="1d")['Close'].iloc[-1])).quantize(Decimal("0.0000001"))
        return (current_price / exchange_rate).quantize(Decimal("0.0000001")) # Maintain precision

    def get_hr_price(self):
        ZSE_XML_URL = os.environ.get("ZSE_XML_URL")
        response = requests.get(ZSE_XML_URL)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch XML data: {response.status_code}")
    
        root = ET.fromstring(response.text)
        if self.type == "stock":
            for secboard in root.findall(".//secboardData/secboard"):
                sec_code = secboard.get("secCode")
                if sec_code is not None and sec_code == self.ticker:
                    last_price = secboard.find("lastPrice")
                    offer_price = secboard.find("offerPrice")
                    bid_price = secboard.find("bidPrice")

                    # Extract values safely
                    last_price = Decimal(last_price.text) if last_price is not None and last_price.text else None
                    offer_price = Decimal(offer_price.text) if offer_price is not None and offer_price.text else None
                    bid_price = Decimal(bid_price.text) if bid_price is not None and bid_price.text else None

                    # Return the first available price
                    return last_price or offer_price or bid_price or None
            
            return None  # Ticker not found
        
        elif self.type == "index":
            for index in root.findall(".//indexData/index"):
                sec_code = index.get("secCode")
                if sec_code is not None and sec_code == self.ticker:
                    value = index.find("value")
                    if value is not None and value.text:
                        return Decimal(value.text)
                    else:
                        return None
        return None
        

    def get_current_value(self):
        """Calculate current market value of this stock holding"""
        return self.quantity * self.get_current_price()
