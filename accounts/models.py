from django.contrib.auth.models import AbstractUser
from django.db import models
import yfinance as yf
from decimal import Decimal

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
    
    def get_current_price(self):
        """Fetch the latest stock price using yfinance"""
        stock = yf.Ticker(self.ticker)
        forex = yf.Ticker("EURUSD=X")
        exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))
        current_price = Decimal(str(stock.history(period="1d")["Close"].iloc[-1])).quantize(Decimal("0.0000001"))
        return (current_price / exchange_rate).quantize(Decimal("0.0000001")) # Maintain precision

    def get_current_value(self):
        """Calculate current market value of this stock holding"""
        return self.quantity * self.get_current_price()
