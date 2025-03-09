from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Portfolio, PortfolioItem
# Register your models here.

class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for managing users.
    """
    model = CustomUser

#admin.site.register(CustomUser, CustomUserAdmin)

class PortfolioItemInline(admin.TabularInline):
    """Allows PortfolioItems to be edited within the Portfolio admin panel."""
    model = PortfolioItem
    extra = 1  # Show one empty row for adding new items

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Customize how Portfolio is displayed in Django Admin."""
    list_display = ("user", "total_value", "cash_balance")  # Show these fields in the list view
    inlines = [PortfolioItemInline]  # Display PortfolioItems inside Portfolio page

    def total_value(self, obj):
        return f"${obj.get_total_value():,.2f}"

    def cash_balance(self, obj):
        return f"${obj.cash_balance:,.2f}"

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("ticker", "quantity", "purchase_price", "current_price", "portfolio")
    list_filter = ("portfolio",)
    search_fields = ("ticker",)

    def current_price(self, obj):
        return f"${obj.get_current_price():,.2f}"  # Calls get_current_price method

admin.site.register(CustomUser)  # Register CustomUser model normally
