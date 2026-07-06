# Mathematical Modeling of a 2x Leveraged ETF Portfolio

## 1. Problem Statement

Design an asset allocation and daily rebalancing model for an idealized
**2x leveraged ETF** tracking an index. The fund must achieve daily 2x exposure
using only **physical equities ($P$)**, **equity futures ($F$)**, and
**cash/liquid collateral ($C$)**.

### Informal Overview

At the close on day $t-1$ the fund holds a known AUM, invested in a physical
stock basket, an index future, and cash/margin, sized to deliver exactly 2x
exposure. Overnight the market moves: each stock drifts by its own return, the
future tracks the index, and a new close is struck on day $t$.

Because the ETF must reset to 2x exposure *every day* while respecting the
exchange-margin and risk-buffer constraints, this price move mechanically forces
a rebalancing trade. The manager must buy (if the index rose) or sell (if it
fell) a basket of stocks in fixed proportions, together with a matching
adjustment to the future. The sizes of these trades are pinned down entirely by
the leverage mechanics and margin rules, and turn out to be linear in the AUM
and in the index return $r$.

The problem therefore boils down to estimating the market-impact cost of trading
a single correlated basket — the stock constituents plus one future. This is
what the **Bouchaud–Benzaquen cross-impact formula** in Section 4 provides.

### Notation

Portfolio variables:

* $\text{AUM}_t$: assets under management at the start of day $t$.
* $S_t^i$: price of stock $i$ at time $t$ (the symbol $S$ denotes stock prices
  only).
* $m$: number of stocks in the replication basket ($i = 1,\ldots,m$).
* $w_i$: weight of stock $i$ in the basket, $\sum_{i=1}^{m} w_i = 1$; stock $i$
  holds dollar value $w_i P_t$.
* $P_t$: total dollar value of the physical-equity basket.
* $F_t$: futures notional exposure.
* $M_t$: exchange margin deposit.
* $C_t$: internal liquid cash buffer.
* $\mu$: exchange margin requirement ($0 < \mu < 1$).
* $V_{\mathrm{max}}$: proxy for the maximum expected daily index drop.
* $r$: index return over trading day 1.
* $r_i = S_2^i/S_1^i - 1$: return of stock $i$ over trading day 1.
* $r_P = \sum_{i} w_i r_i$: physical-basket return; $r_P = r$ under exact index
  replication.

Market-impact variables:

* $N_P, N_F$: absolute aggregate executed notionals for physical equities and
  futures; stock $i$ receives traded notional $w_i N_P$.
* $\sigma_i$: annualized volatility of stock $i$.
* $\sigma_F$: annualized volatility of the futures/index exposure.
* $\sigma_i^{\mathrm{daily}} = \sigma_i / \sqrt{252}$ and
  $\sigma_F^{\mathrm{daily}} = \sigma_F / \sqrt{252}$: daily volatilities.
* $T_i, T_F$: average daily turnover for stock $i$ and futures.
* $\mathbf{q}$: signed rebalancing-notional vector over all traded assets.
* $\mathbf{v}$: average-daily-turnover vector matching $\mathbf{q}$.
* $\mathbf{R}$: correlation matrix of all traded assets (renamed from the
  cross-impact $\mathbf{C}$ matrix to avoid collision with the cash variable
  $C_t$).
* $\gamma$: market-impact calibration constant.
* $\alpha$: impact exponent, typically near $1/2$.

### Constraints

| Constraint | Formula |
| --- | ---: |
| Total exposure | $P_t + F_t = 2 \cdot \text{AUM}_t$ |
| Balance sheet | $P_t + M_t + C_t = \text{AUM}_t$ |
| Exchange margin | $M_t = \mu \cdot F_t$ |
| Risk buffer | $C_t = V_{\mathrm{max}} \cdot F_t$ |

---

## 2. Initial Portfolio Allocation (Day 1)

Define $K$ as the required futures exposure per dollar of AUM:

$$K = \frac{1}{(1 - \mu) - V_{\mathrm{max}}}$$

Substituting the margin and buffer rules into the balance sheet gives:

$$
\begin{aligned}
P_1 + \mu F_1 + V_{\mathrm{max}}F_1 &= \text{AUM}_1 \\
\implies P_1 + (\mu + V_{\mathrm{max}})F_1 &= \text{AUM}_1
\end{aligned}
$$

Using $P_1 = 2\text{AUM}_1 - F_1$, the Day 1 target holdings are:

| Holding | Day 1 value |
| --- | ---: |
| Futures notional | $F_1 = K \cdot \text{AUM}_1$ |
| Physical equities | $P_1 = (2 - K) \cdot \text{AUM}_1$ |
| Internal cash buffer | $C_1 = V_{\mathrm{max}} \cdot K \cdot \text{AUM}_1$ |
| Exchange margin deposit | $M_1 = \mu \cdot K \cdot \text{AUM}_1$ |

### Case $V_{\mathrm{max}} = \mu$

If the internal risk buffer equals the exchange margin rate, then

$$K = \frac{1}{1 - 2\mu} \quad \text{with } \mu < \frac{1}{2}.$$

The allocation simplifies to:

| Holding | Value when $V_{\mathrm{max}} = \mu$ |
| --- | ---: |
| Futures notional | $F_1 = \frac{\text{AUM}_1}{1 - 2\mu}$ |
| Physical equities | $P_1 = \left(2 - \frac{1}{1 - 2\mu}\right)\text{AUM}_1$ |
| Internal cash buffer | $C_1 = \frac{\mu}{1 - 2\mu}\text{AUM}_1$ |
| Exchange margin deposit | $M_1 = \frac{\mu}{1 - 2\mu}\text{AUM}_1$ |

---

## 3. Daily Rebalancing

If the index returns $r$, the 2x fund value becomes:

$$\text{AUM}_2 = \text{AUM}_1(1 + 2r)$$

### Before Rebalancing

Before the close, each holding moves by its own return:

* Stock $i$: its dollar holding $w_i P_1$ grows to $w_i P_1(1 + r_i)$.
* Physical basket (organic): summing over stocks,
  $P_{\text{organic}} = \sum_i w_i P_1(1 + r_i) = P_1(1 + r_P)$, which equals
  $P_1(1 + r)$ under exact index replication ($r_P = r$).
* Futures: the notional exposure scales to $F_1(1 + r)$, with realized cash P&L
  $F_1 \cdot r$.

### Target Day 2 Values

To keep 2x leverage on the new AUM:

* $F_2 = K \cdot \text{AUM}_2 = K \cdot \text{AUM}_1(1 + 2r)$
* $P_2 = (2 - K) \cdot \text{AUM}_2 = (2 - K) \cdot \text{AUM}_1(1 + 2r)$

### Active Rebalancing Trades

The closing trades bridge organic end-of-day values and Day 2 targets:

<!-- markdownlint-disable MD013 -->
| Trade | Organic value | Target value | Executed amount |
| --- | ---: | ---: | ---: |
| Physical equities | $P_1(1 + r)$ | $P_2 = P_1(1 + 2r)$ | $\text{d}P = P_2 - P_1(1 + r) = P_1r = \left(2 - \frac{1}{(1 - \mu) - V_{\mathrm{max}}}\right)\text{AUM}_1r$ |
| Futures | $F_1(1 + r)$ | $F_2 = F_1(1 + 2r)$ | $\text{d}F = F_2 - F_1(1 + r) = F_1r = \left(\frac{\text{AUM}_1}{(1 - \mu) - V_{\mathrm{max}}}\right)r$ |
<!-- markdownlint-enable MD013 -->

## 4. Market-Impact Transaction Costs

Treat the stock constituents and futures contract as one correlated traded asset
universe. Let the signed rebalancing vector be

$$
\mathbf{q}
= (q_1,\ldots,q_m,q_F)^\top,
\qquad
q_i = w_i\,\text{d}P,
\qquad
q_F = \text{d}F.
$$

The per-stock split $q_i = w_i\,\text{d}P$ uses day-1 weights; the intraday
weight drift is $O(r)$, so it only perturbs $q_i$ at order $O(r^2)$ and is
neglected.

The corresponding turnover vector and daily-volatility diagonal matrix are

$$
\mathbf{v} = (T_1,\ldots,T_m,T_F)^\top,
\qquad
\mathbf{D}_{\sigma}
= \operatorname{diag}(\sigma_1^{\mathrm{daily}},\ldots,
\sigma_m^{\mathrm{daily}},\sigma_F^{\mathrm{daily}}).
$$

Using the Bouchaud–Benzaken cross-impact formula, the market-impact cost in bp
for each traded asset is

$$
\mathbf{I}^{\mathrm{bp}}
= 10^4\gamma\,\mathbf{D}_{\sigma}\,\mathbf{R}^{1-\alpha}
\left[
\operatorname{sign}(\mathbf{q}) \odot
\left|\mathbf{R}^{\alpha}\left(\frac{\mathbf{q}}{\mathbf{v}}\right)\right|^{\alpha}
\right].
$$

Division, absolute value, powers, signs, and $\odot$ are element-wise except for
the matrix powers of $\mathbf{R}$. The entries of $\mathbf{q}$ are:

<!-- markdownlint-disable MD013 -->
| Rebalanced leg | Signed vector entry | Absolute notional |
| --- | ---: | ---: |
| Stock $i$ | $q_i = w_i\left(2 - \frac{1}{(1 - \mu) - V_{\mathrm{max}}}\right)\text{AUM}_1r$ | $\lvert q_i\rvert = w_iN_P$ |
| Futures | $q_F = \frac{\text{AUM}_1r}{(1 - \mu) - V_{\mathrm{max}}}$ | $N_F = \lvert q_F\rvert$ |
<!-- markdownlint-enable MD013 -->

With this sign convention, the total market-impact cost in USD is

$$
\operatorname{tcost}^{\mathrm{USD}}
= \frac{\mathbf{q}^{\top}\mathbf{I}^{\mathrm{bp}}}{10^4}.
$$

Equivalently, by components,

$$
\operatorname{tcost}^{\mathrm{USD}}
= \frac{1}{10^4}
\left(\sum_i q_i I_i^{\mathrm{bp}} + q_F I_F^{\mathrm{bp}}\right).
$$

## 5. Operational Conclusion

Both active trades scale **linearly** with $\text{AUM}_1$ and $r$.

* If $r > 0$, the manager **buys** both physical equities and futures.
* If $r < 0$, the manager **sells** both physical equities and futures.
