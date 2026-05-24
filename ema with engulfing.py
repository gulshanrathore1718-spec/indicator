//@version=5
indicator("EMA Trend + Engulfing Signal", overlay=true, max_labels_count=500)

// ─── INPUTS ───────────────────────────────────────────────
ema9_len   = input.int(9,   "Fast EMA",   minval=1)
ema21_len  = input.int(21,  "Mid EMA",    minval=1)
ema100_len = input.int(100, "Slow EMA",   minval=1)
angleMin   = input.float(30.0, "Min EMA Angle (degrees)", minval=1.0, maxval=89.0)
angleLookback = input.int(5, "Angle Lookback (bars)", minval=2, maxval=20)

// ─── EMA CALCULATIONS ─────────────────────────────────────
ema9   = ta.ema(close, ema9_len)
ema21  = ta.ema(close, ema21_len)
ema100 = ta.ema(close, ema100_len)

// ─── PLOT EMAs ────────────────────────────────────────────
plot(ema9,   "EMA 9",   color=color.new(color.aqua,   0), linewidth=1)
plot(ema21,  "EMA 21",  color=color.new(color.orange, 0), linewidth=2)
plot(ema100, "EMA 100", color=color.new(color.white,  20), linewidth=2)

// ─── EMA ANGLE CALCULATION ────────────────────────────────
// Uses atan of (EMA change over N bars) normalized to price scale
ema9_angle  = math.abs(math.atan((ema9  - ema9[angleLookback])  / (ema9[angleLookback]  * angleLookback / 100)) * (180 / math.pi))
ema21_angle = math.abs(math.atan((ema21 - ema21[angleLookback]) / (ema21[angleLookback] * angleLookback / 100)) * (180 / math.pi))

// ─── TREND CONDITIONS ─────────────────────────────────────
bullTrend = ema9 > ema100 and ema21 > ema100 and ema9 > ema21
bearTrend = ema9 < ema100 and ema21 < ema100 and ema9 < ema21

// Angle filter — both short EMAs must be sloping steeply enough
bullAngleOK = ema9_angle >= angleMin and ema21_angle >= angleMin and ema9 > ema9[1] and ema21 > ema21[1]
bearAngleOK = ema9_angle >= angleMin and ema21_angle >= angleMin and ema9 < ema9[1] and ema21 < ema21[1]

// ─── PULLBACK DETECTION ───────────────────────────────────
// Price pulled back toward EMAs (touched or came near 21 EMA)
bullPullback = low[1] <= ema21[1] * 1.002 or (close[1] < ema9[1])
bearPullback = high[1] >= ema21[1] * 0.998 or (close[1] > ema9[1])

// ─── 2-CANDLE CLASSIC ENGULFING ───────────────────────────
// Bullish engulfing: prev candle bearish, current candle bullish & body engulfs prev body
prevBearish   = close[1] < open[1]
currBullish   = close    > open
bullEngulf    = prevBearish and currBullish
             and open  <= close[1]
             and close >= open[1]

// Bearish engulfing: prev candle bullish, current candle bearish & body engulfs prev body
prevBullish   = close[1] > open[1]
currBearish   = close    < open
bearEngulf    = prevBullish and currBearish
             and open  >= close[1]
             and close <= open[1]

// ─── FINAL SIGNALS ────────────────────────────────────────
buySignal  = bullTrend and bullAngleOK and bullPullback and bullEngulf
sellSignal = bearTrend and bearAngleOK and bearPullback and bearEngulf

// ─── PLOT SIGNALS ─────────────────────────────────────────
plotshape(buySignal,
     title="BUY",
     location=location.belowbar,
     style=shape.labelup,
     color=color.new(color.lime, 0),
     textcolor=color.black,
     text="BUY",
     size=size.normal)

plotshape(sellSignal,
     title="SELL",
     location=location.abovebar,
     style=shape.labeldown,
     color=color.new(color.red, 0),
     textcolor=color.white,
     text="SELL",
     size=size.normal)

// ─── BACKGROUND HIGHLIGHT when trend is active ────────────
bgcolor(bullTrend and bullAngleOK ? color.new(color.lime, 94) : na, title="Bull Trend BG")
bgcolor(bearTrend and bearAngleOK ? color.new(color.red,  94) : na, title="Bear Trend BG")

// ─── ALERTS ───────────────────────────────────────────────
alertcondition(buySignal,  "BUY Signal",  "EMA Trend: Bullish Engulfing BUY setup triggered!")
alertcondition(sellSignal, "SELL Signal", "EMA Trend: Bearish Engulfing SELL setup triggered!")