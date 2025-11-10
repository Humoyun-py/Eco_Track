from datetime import datetime

def format_date(date_string):
    """Format date to readable string"""
    if isinstance(date_string, str):
        date_obj = datetime.fromisoformat(date_string)
    else:
        date_obj = date_string
    
    return date_obj.strftime("%Y-%m-%d %H:%M")

def calculate_level(streak):
    """Calculate user level based on streak"""
    return (streak // 7) + 1

def format_coins(coins):
    """Format coins with emoji"""
    return f"💰 {coins}"

def format_energy(energy):
    """Format energy with emoji"""
    return f"⚡ {energy}/100"

def format_streak(streak):
    """Format streak with emoji"""
    return f"🔥 {streak} kun"