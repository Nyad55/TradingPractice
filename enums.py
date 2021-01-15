from enum import Enum


class TradeMode(Enum):
    """Enum for selecting the mode of the trade"""
    BUY = 1
    SELL = 2
    CLOSED = 3

class TradeType(Enum):
    """Enum for selecting what type of trade is placed"""
    TREND = 1
    FADE = 2

class TradeState:
    """"Keeps track of the current state"""
    equity = 100
    profit = 0
    trade_mode = TradeMode.CLOSED
    order_price = 0
    position_size = 0
    stop_loss_price = 0
    pips = 0
    trade_type = TradeType.TREND
    candle_number = 0

class Stats:
    """Tracks the different types of trade pip wins and losses for statistical analysis"""
    trend = []
    fade = []

class OHLC(Enum):
    """Enum for picking Open High Low Close data from the bid and ask lists"""
    OPENINDEX = 1
    HIGHINDEX = 2
    LOWINDEX = 3
    CLOSEINDEX = 4