"""
Enhanced Trading Signal Module

Implements advanced trading logic from:
- Jesse Livermore (pyramiding & position management)
- ATR-based risk management
- Options analysis and recommendations
- Advanced Volume Price Analysis
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
import json
import os
from datetime import datetime, timedelta


@dataclass
class ATRData:
    """Average True Range data for volatility measurement"""
    atr: float
    atr_percent: float  # ATR as % of price
    
    
@dataclass
class RiskMetrics:
    """Risk management calculations"""
    entry_price: float
    atr_stop: float  # ATR-based stop loss
    stop_distance_pct: float
    position_size_pct: float  # % of portfolio for 1% risk
    risk_reward_ratio: float
    target_1: float  # 2x ATR target
    target_2: float  # 3x ATR target
    target_3: float  # 5x ATR target


@dataclass
class OptionsRecommendation:
    """Options trade recommendation"""
    strategy: str  # "CALL", "CALL_SPREAD", "SHARES_THEN_CALLS"
    strike: float
    expiry_days: int
    reasoning: str
    iv_percentile: Optional[float] = None


@dataclass
class VPAAnalysis:
    """Advanced Volume Price Analysis"""
    volume_type: str  # "CLIMAX", "BACKGROUND", "RISING", "FALLING"
    effort_vs_result: str  # "BULLISH", "BEARISH", "NEUTRAL"
    volume_trend: str  # "INCREASING", "DECREASING", "STEADY"
    strength_score: float  # 0-10 scale


@dataclass
class PyramidSignal:
    """Livermore-style pyramiding signal"""
    action: str  # "INITIAL", "ADD_25%", "ADD_50%", "HOLD", "EXIT"
    reasoning: str
    current_profit_pct: float
    suggested_add_price: Optional[float] = None


@dataclass
class EnhancedSignal:
    """Enhanced trading signal with all analysis"""
    ticker: str
    interval: str
    price: float
    time: str
    
    # Original breakout data
    range_pct: float
    volume_multiple: float
    
    # Risk management
    atr_data: ATRData
    risk_metrics: RiskMetrics
    
    # VPA
    vpa_analysis: VPAAnalysis
    
    # Options
    options_rec: OptionsRecommendation
    
    # Pyramiding
    pyramid_signal: PyramidSignal
    
    # Overall score
    signal_strength: float  # 0-100


class PositionTracker:
    """Track open positions for pyramiding logic"""
    
    def __init__(self, db_file: str = "positions.json"):
        self.db_file = db_file
        self.positions: Dict = self._load_positions()
    
    def _load_positions(self) -> Dict:
        """Load positions from file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_positions(self):
        """Save positions to file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def add_position(self, ticker: str, entry_price: float, entry_time: str, 
                     interval: str, stop_loss: float):
        """Add new position"""
        self.positions[ticker] = {
            "entry_price": entry_price,
            "entry_time": entry_time,
            "interval": interval,
            "stop_loss": stop_loss,
            "adds": [],  # Track pyramid additions
            "highest_price": entry_price,
            "status": "ACTIVE"
        }
        self._save_positions()
    
    def update_position(self, ticker: str, current_price: float):
        """Update position with current price"""
        if ticker in self.positions:
            pos = self.positions[ticker]
            pos["highest_price"] = max(pos["highest_price"], current_price)
            pos["last_update"] = datetime.now().isoformat()
            self._save_positions()
    
    def add_pyramid(self, ticker: str, add_price: float, add_pct: float):
        """Record pyramid addition"""
        if ticker in self.positions:
            self.positions[ticker]["adds"].append({
                "price": add_price,
                "percent": add_pct,
                "time": datetime.now().isoformat()
            })
            self._save_positions()
    
    def close_position(self, ticker: str, exit_price: float, reason: str):
        """Close position"""
        if ticker in self.positions:
            self.positions[ticker]["status"] = "CLOSED"
            self.positions[ticker]["exit_price"] = exit_price
            self.positions[ticker]["exit_reason"] = reason
            self.positions[ticker]["exit_time"] = datetime.now().isoformat()
            self._save_positions()
    
    def get_position(self, ticker: str) -> Optional[Dict]:
        """Get position data"""
        return self.positions.get(ticker)
    
    def has_active_position(self, ticker: str) -> bool:
        """Check if ticker has active position"""
        pos = self.positions.get(ticker)
        return pos is not None and pos.get("status") == "ACTIVE"


def calculate_atr(candles: List, period: int = 14) -> ATRData:
    """Calculate Average True Range"""
    if len(candles) < period + 1:
        # Not enough data, use simple range
        recent = candles[-period:]
        avg_range = sum(c.high - c.low for c in recent) / len(recent)
        current_price = candles[-1].close
        return ATRData(
            atr=avg_range,
            atr_percent=(avg_range / current_price * 100) if current_price > 0 else 0
        )
    
    true_ranges = []
    for i in range(1, len(candles)):
        high = candles[i].high
        low = candles[i].low
        prev_close = candles[i-1].close
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)
    
    # Simple moving average of true ranges
    atr = sum(true_ranges[-period:]) / period
    current_price = candles[-1].close
    
    return ATRData(
        atr=atr,
        atr_percent=(atr / current_price * 100) if current_price > 0 else 0
    )


def calculate_risk_metrics(price: float, atr_data: ATRData, 
                           atr_multiplier: float = 2.0) -> RiskMetrics:
    """Calculate risk management metrics"""
    atr = atr_data.atr
    
    # Stop loss at 2x ATR below entry
    stop_loss = price - (atr * atr_multiplier)
    stop_distance_pct = ((price - stop_loss) / price) * 100
    
    # Position sizing for 1% account risk
    # If risking 1% of account, position size = 1% / stop_distance_pct
    position_size_pct = min(1.0 / stop_distance_pct * 100, 25.0)  # Max 25% position
    
    # Targets based on ATR
    target_1 = price + (atr * 2)  # 2R
    target_2 = price + (atr * 3)  # 3R
    target_3 = price + (atr * 5)  # 5R
    
    # Risk/reward to first target
    risk = price - stop_loss
    reward = target_1 - price
    rr_ratio = reward / risk if risk > 0 else 0
    
    return RiskMetrics(
        entry_price=price,
        atr_stop=stop_loss,
        stop_distance_pct=stop_distance_pct,
        position_size_pct=position_size_pct,
        risk_reward_ratio=rr_ratio,
        target_1=target_1,
        target_2=target_2,
        target_3=target_3
    )


def analyze_vpa_advanced(candles: List, volume_multiple: float) -> VPAAnalysis:
    """Advanced Volume Price Analysis"""
    if len(candles) < 20:
        return VPAAnalysis(
            volume_type="UNKNOWN",
            effort_vs_result="NEUTRAL",
            volume_trend="STEADY",
            strength_score=5.0
        )
    
    recent_candles = candles[-20:]
    last_candle = candles[-1]
    
    # Volume classification
    if volume_multiple >= 3.0:
        volume_type = "CLIMAX"
    elif volume_multiple >= 1.5:
        volume_type = "RISING"
    elif volume_multiple <= 0.7:
        volume_type = "BACKGROUND"
    else:
        volume_type = "STEADY"
    
    # Effort vs Result (Anna Coulling)
    price_range = last_candle.high - last_candle.low
    avg_range = sum(c.high - c.low for c in recent_candles[:-1]) / len(recent_candles[:-1])
    
    # High volume + small range = potential reversal (effort without result)
    # High volume + large range = strong move (effort with result)
    if volume_multiple >= 2.0:
        if price_range > avg_range * 1.5:
            effort_vs_result = "BULLISH"  # High volume, wide range
            strength = 8.0
        elif price_range < avg_range * 0.7:
            effort_vs_result = "BEARISH"  # High volume, narrow range (absorption)
            strength = 3.0
        else:
            effort_vs_result = "NEUTRAL"
            strength = 5.0
    else:
        effort_vs_result = "NEUTRAL"
        strength = 5.0
    
    # Volume trend
    early_vol = sum(c.volume for c in recent_candles[:10]) / 10
    late_vol = sum(c.volume for c in recent_candles[-10:]) / 10
    
    if late_vol > early_vol * 1.3:
        volume_trend = "INCREASING"
        strength += 1.0
    elif late_vol < early_vol * 0.7:
        volume_trend = "DECREASING"
        strength -= 1.0
    else:
        volume_trend = "STEADY"
    
    return VPAAnalysis(
        volume_type=volume_type,
        effort_vs_result=effort_vs_result,
        volume_trend=volume_trend,
        strength_score=min(10.0, max(0.0, strength))
    )


def generate_options_recommendation(price: float, atr_data: ATRData, 
                                    interval: str) -> OptionsRecommendation:
    """Generate options trading recommendation"""
    atr_pct = atr_data.atr_percent
    
    # Determine strategy based on volatility and timeframe
    if interval == "1min":
        # Fast moves - consider shares first, then calls
        strategy = "SHARES_THEN_CALLS"
        expiry_days = 7  # Weekly options
        reasoning = "Fast 1m breakout - enter with shares, add calls on confirmation"
    elif interval == "5min":
        # Intraday - ATM or slightly OTM calls
        if atr_pct > 3.0:  # High volatility
            strategy = "CALL_SPREAD"
            expiry_days = 14
            reasoning = "High volatility - use call spread to reduce cost"
        else:
            strategy = "CALL"
            expiry_days = 14
            reasoning = "Clean breakout - ATM calls for leverage"
    else:  # 15min+
        # Swing - give it time
        strategy = "CALL"
        expiry_days = 30
        reasoning = "Swing setup - use monthly calls for time"
    
    # Strike selection: ATM to 5% OTM
    if strategy == "CALL_SPREAD":
        strike = price * 1.02  # 2% OTM
    else:
        strike = price * 1.00  # ATM
    
    return OptionsRecommendation(
        strategy=strategy,
        strike=strike,
        expiry_days=expiry_days,
        reasoning=reasoning,
        iv_percentile=None  # Would need options data API
    )


def generate_pyramid_signal(ticker: str, current_price: float, 
                            position_tracker: PositionTracker,
                            atr_data: ATRData) -> PyramidSignal:
    """Generate Livermore-style pyramiding signal"""
    
    if not position_tracker.has_active_position(ticker):
        # Initial entry
        return PyramidSignal(
            action="INITIAL",
            reasoning="New breakout - initial entry opportunity",
            current_profit_pct=0.0,
            suggested_add_price=None
        )
    
    pos = position_tracker.get_position(ticker)
    entry_price = pos["entry_price"]
    profit_pct = ((current_price - entry_price) / entry_price) * 100
    
    # Livermore: Add to winners, cut losers
    if profit_pct < -2.0:
        return PyramidSignal(
            action="EXIT",
            reasoning="Position against us - cut loss per Livermore",
            current_profit_pct=profit_pct
        )
    
    # Add on strength (profit + new high)
    num_adds = len(pos.get("adds", []))
    
    if profit_pct >= 10.0 and num_adds == 0:
        # First add at +10%
        return PyramidSignal(
            action="ADD_25%",
            reasoning="Strong move +10% - add 25% to winner (Livermore)",
            current_profit_pct=profit_pct,
            suggested_add_price=current_price
        )
    elif profit_pct >= 20.0 and num_adds == 1:
        # Second add at +20%
        return PyramidSignal(
            action="ADD_50%",
            reasoning="Exceptional move +20% - final add 50% (Livermore)",
            current_profit_pct=profit_pct,
            suggested_add_price=current_price
        )
    elif profit_pct >= 5.0:
        return PyramidSignal(
            action="HOLD",
            reasoning=f"In profit +{profit_pct:.1f}% - let it run",
            current_profit_pct=profit_pct
        )
    else:
        return PyramidSignal(
            action="HOLD",
            reasoning="Early in trade - monitor",
            current_profit_pct=profit_pct
        )


def calculate_signal_strength(vpa: VPAAnalysis, risk_metrics: RiskMetrics,
                              volume_multiple: float, range_pct: float) -> float:
    """Calculate overall signal strength 0-100"""
    score = 50.0  # Base score
    
    # VPA contribution (0-20 points)
    score += (vpa.strength_score - 5.0) * 2  # -10 to +10
    
    # Volume contribution (0-20 points)
    if volume_multiple >= 3.0:
        score += 20
    elif volume_multiple >= 2.0:
        score += 15
    elif volume_multiple >= 1.5:
        score += 10
    
    # Tight base contribution (0-15 points)
    if range_pct <= 1.0:
        score += 15
    elif range_pct <= 2.0:
        score += 10
    elif range_pct <= 3.0:
        score += 5
    
    # Risk/reward contribution (0-15 points)
    if risk_metrics.risk_reward_ratio >= 3.0:
        score += 15
    elif risk_metrics.risk_reward_ratio >= 2.0:
        score += 10
    elif risk_metrics.risk_reward_ratio >= 1.5:
        score += 5
    
    return min(100.0, max(0.0, score))
