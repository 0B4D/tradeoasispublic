import yfinance as yf
from django.core.management.base import BaseCommand
from stock.models import Stock
from stock.stocks import get_sp500_tickers

# List of stock tickers to fetch
STOCK_TICKERS = get_sp500_tickers()

class Command(BaseCommand):
    help = "Fetch stock data and store it in the database"

    def handle(self, *args, **kwargs):
        for ticker in STOCK_TICKERS:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # Extract relevant details
                name = info.get("shortName", ticker)
                sector = info.get("sector", "Unknown")
                industry = info.get("industry", "Unknown")
                short_info = info.get("longBusinessSummary", "No description available.")
                market_cap = info.get("marketCap", None)
                country = info.get("country", "Unknown")
                website = info.get("website", None)
                employees = info.get("fullTimeEmployees", None)

                # Create or update stock record
                stock_obj, created = Stock.objects.update_or_create(
                    ticker=ticker,
                    defaults={
                        "name": name,
                        "sector": sector,
                        "industry": industry,
                        "short_info": short_info,
                        "market_cap": market_cap,
                        "country": country,
                        "website": website,
                        "full_time_employees": employees,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added new stock: {name} ({ticker})"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated stock: {name} ({ticker})"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to fetch {ticker}: {e}"))
