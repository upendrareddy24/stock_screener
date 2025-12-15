"""
Enhanced Alert Formatter

Creates detailed, educational Telegram alerts explaining WHY each signal triggered.
Includes volume flow analysis, EMA details, breakout mechanics, and trade reasoning.
"""

from enhanced_signals import EnhancedSignal


def format_detailed_alert(sig: EnhancedSignal) -> str:
    """
    Create comprehensive alert with full breakout explanation.
    
    Explains:
    - Why this stock was selected
    - Volume flow analysis
    - EMA alignment details
    - Breakout mechanics
    - Risk/reward setup
    - Trading plan
    """
    
    # Volume analysis explanation
    vol_explanation = _explain_volume(sig.volume_multiple, sig.vpa_analysis.volume_type)
    
    # EMA trend explanation
    ema_explanation = _explain_ema_trend()
    
    # Breakout type
    breakout_type = _identify_breakout_type(sig.range_pct, sig.volume_multiple)
    
    # Pyramid emoji
    pyramid_emoji = {
        "INITIAL": "🆕",
        "ADD_25%": "📈",
        "ADD_50%": "🚀",
        "HOLD": "💎",
        "EXIT": "🚪"
    }.get(sig.pyramid_signal.action, "")
    
    # Build comprehensive alert
    msg = (
        f"🚨 *BREAKOUT ALERT* 🚨\n"
        f"Score: *{sig.signal_strength:.0f}/100* | {_score_rating(sig.signal_strength)}\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *{sig.ticker}* @ ${sig.price:.2f}\n"
        f"⏰ {sig.time}\n"
        f"📍 Timeframe: {sig.interval} | Tier: {sig.tier}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        f"🎯 *WHY THIS ALERT?*\n\n"
        
        f"*{breakout_type}*\n\n"
        
        f"*1️⃣ ACCUMULATION PHASE (Wyckoff)*\n"
        f"• Tight {sig.range_pct:.1f}% consolidation range\n"
        f"• 20-bar base building (accumulation)\n"
        f"• Price coiled like a spring ⚡\n"
        f"• Smart money accumulating position\n\n"
        
        f"*2️⃣ VOLUME CONFIRMATION (VPA)*\n"
        f"• Current volume: *{sig.volume_multiple:.1f}x average*\n"
        f"• Volume type: *{sig.vpa_analysis.volume_type}*\n"
        f"• {vol_explanation}\n"
        f"• Effort vs Result: *{sig.vpa_analysis.effort_vs_result}*\n"
        f"• Volume trend: {sig.vpa_analysis.volume_trend}\n\n"
        
        f"*3️⃣ TREND ALIGNMENT (Murphy)*\n"
        f"{ema_explanation}\n"
        f"• All EMAs stacked bullish 📈\n"
        f"• Price above all moving averages\n"
        f"• Strong uptrend confirmed ✅\n\n"
        
        f"*4️⃣ PRICE ACTION (Brooks)*\n"
        f"• Bullish breakout candle (close > open)\n"
        f"• Strong close above range high\n"
        f"• Break of structure confirmed\n"
        f"• No weak/indecision bars\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ *RISK MANAGEMENT*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        f"*Entry & Stops:*\n"
        f"• Entry: ${sig.risk_metrics.entry_price:.2f}\n"
        f"• Stop Loss: ${sig.risk_metrics.atr_stop:.2f}\n"
        f"• Risk: {sig.risk_metrics.stop_distance_pct:.1f}% ({sig.atr_data.atr:.2f} ATR)\n"
        f"• R:R Ratio: *{sig.risk_metrics.risk_reward_ratio:.1f}:1*\n\n"
        
        f"*Profit Targets:*\n"
        f"• Target 1: ${sig.risk_metrics.target_1:.2f} (2R) 🎯\n"
        f"• Target 2: ${sig.risk_metrics.target_2:.2f} (3R) 🎯🎯\n"
        f"• Target 3: ${sig.risk_metrics.target_3:.2f} (5R) 🎯🎯🎯\n\n"
        
        f"*Position Sizing:*\n"
        f"• Recommended: *{sig.risk_metrics.position_size_pct:.1f}%* of portfolio\n"
        f"• (Calculated for 1% account risk)\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 *OPTIONS STRATEGY*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        f"*Recommendation:* {sig.options_rec.strategy}\n"
        f"• Strike: ${sig.options_rec.strike:.0f}\n"
        f"• Expiry: {sig.options_rec.expiry_days} days\n"
        f"• Why: {sig.options_rec.reasoning}\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{pyramid_emoji} *LIVERMORE PLAN*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        f"*Action:* {sig.pyramid_signal.action}\n"
        f"• {sig.pyramid_signal.reasoning}\n"
    )
    
    # Add pyramid plan if initial entry
    if sig.pyramid_signal.action == "INITIAL":
        msg += (
            f"\n*Pyramiding Plan:*\n"
            f"• Initial: 100% position now\n"
            f"• Add 25% if +10% profit\n"
            f"• Add 50% if +20% profit\n"
            f"• Exit if -2% (cut losers fast)\n"
        )
    elif sig.pyramid_signal.action in ["ADD_25%", "ADD_50%"]:
        msg += (
            f"\n*Current Profit:* +{sig.pyramid_signal.current_profit_pct:.1f}%\n"
            f"• This is a WINNER - add to it!\n"
        )
    
    msg += (
        f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 *TRADE SUMMARY*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        f"This is a *{breakout_type.lower()}* with:\n"
        f"✅ Wyckoff accumulation base\n"
        f"✅ {sig.volume_multiple:.1f}x volume spike\n"
        f"✅ EMA trend alignment\n"
        f"✅ Strong price action\n"
        f"✅ {sig.risk_metrics.risk_reward_ratio:.1f}:1 risk/reward\n\n"
        
        f"_Strategy: Enter on breakout, stop below base, "
        f"targets at 2R/3R/5R. Add to winners per Livermore._\n\n"
        
        f"⚡ *Take action or set alerts!* ⚡"
    )
    
    return msg


def _explain_volume(vol_multiple: float, vol_type: str) -> str:
    """Explain volume significance"""
    if vol_multiple >= 3.0:
        return (
            f"MASSIVE {vol_multiple:.1f}x volume spike!\n"
            f"  This is institutional buying (climax volume).\n"
            f"  Big money is entering - follow the smart money!"
        )
    elif vol_multiple >= 2.0:
        return (
            f"Strong {vol_multiple:.1f}x volume increase.\n"
            f"  Confirms breakout validity.\n"
            f"  Institutions are participating."
        )
    else:
        return (
            f"{vol_multiple:.1f}x volume (above average).\n"
            f"  Sufficient for breakout confirmation."
        )


def _explain_ema_trend() -> str:
    """Explain EMA alignment"""
    return (
        "• 20 EMA > 50 EMA > 200 EMA\n"
        "  (Short-term leading long-term)\n"
        "• Price trading above 20 EMA\n"
        "  (Pullbacks are buying opportunities)"
    )


def _identify_breakout_type(range_pct: float, vol_multiple: float) -> str:
    """Identify type of breakout"""
    if range_pct <= 1.5 and vol_multiple >= 3.0:
        return "EXPLOSIVE BREAKOUT FROM TIGHT BASE"
    elif range_pct <= 2.0 and vol_multiple >= 2.5:
        return "STRONG BREAKOUT WITH VOLUME"
    elif range_pct <= 3.0 and vol_multiple >= 2.0:
        return "CLEAN BREAKOUT SETUP"
    else:
        return "BREAKOUT PATTERN"


def _score_rating(score: float) -> str:
    """Convert score to rating"""
    if score >= 85:
        return "EXCEPTIONAL 🔥🔥🔥"
    elif score >= 75:
        return "STRONG 🔥🔥"
    elif score >= 65:
        return "GOOD 🔥"
    else:
        return "MARGINAL"


# Example usage
if __name__ == "__main__":
    print("Enhanced Alert Formatter")
    print("Provides detailed breakout explanations")
