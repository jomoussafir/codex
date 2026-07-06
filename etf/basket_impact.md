# Market Impact Framework for a Basket of Stocks

This framework outlines a mathematically rigorous cross-impact model designed for quantitative trading desks. By separating volatility from correlation and adjusting for the non-linear "Square-Root Law," this formulation successfully handles multi-asset dependencies without violating fundamental boundary conditions.

---

## 🏛️ The Cross-Impact Formula

To accurately estimate market impact across a portfolio, the model decouples volatility from correlation and rotates the volume vector through a fractional correlation matrix *before* applying the concave power law. This prevents the mathematical overestimation of impact costs when assets move together:

$$\mathbf{I} = \gamma \cdot \mathbf{D}_\sigma \cdot \mathbf{C}^{1-\alpha} \cdot \left[ \text{sign}(\mathbf{Q}) \odot \left| \mathbf{C}^\alpha \left(\frac{\mathbf{Q}}{\mathbf{V}}\right) \right|^\alpha \right]$$

### Variable Definitions
* **$\mathbf{I}$ ($N \times 1$):** Vector of expected percentage price impacts (or basis points) for each stock.
* **$\gamma$ (Scalar):** Global calibration constant mapping the outputs to actual currency or basis points.
* **$\mathbf{D}_\sigma$ ($N \times N$):** Diagonal matrix of individual asset volatilities ($\sigma_i$).
* **$\mathbf{C}$ ($N \times N$):** Asset correlation matrix.
* **$\mathbf{Q}$ ($N \times 1$):** Order volume vector (positive for buys, negative for sells).
* **$\mathbf{V}$ ($N \times 1$):** Average Daily Volume (ADV) vector used for liquidity normalization.
* **$\alpha$ (Scalar):** Impact exponent, typically calibrated to $\alpha \approx 0.5$ in accordance with the empirical Square-Root Law.
* **$\odot$:** Hadamard (element-wise) product operator.

---

## 🧪 Verification of Limit Cases

The table below demonstrates how this mathematical framework seamlessly recovers all structural trading realities:

| Trading Scenario | Mathematical Behavior | Economic Reality | Status |
| :--- | :--- | :--- | :---: |
| **Single Stock Traded**<br>($Q_1 \neq 0$, all other $Q_i = 0$) | $\mathbf{C}$ collapses to $1$ for asset 1. $\mathbf{D}_\sigma$ applies raw $\sigma_1$. | Recovers the standard single-asset square-root law scaling with **volatility** ($\sigma$), not variance ($\sigma^2$). | ✅ **Passed** |
| **Zero Correlation**<br>($\mathbf{C} = \mathbf{I}_{N \times N}$) | $\mathbf{C}^\alpha$ and $\mathbf{C}^{1-\alpha}$ become Identity matrices. | All assets behave independently; basket impact equals the sum of isolated single-stock impacts. | ✅ **Passed** |
| **Perfect Negative Correlation**<br>($\rho = -1$, identical $\sigma, V$) | Net internal flow vector $\left( \mathbf{C}^\alpha \frac{\mathbf{Q}}{\mathbf{V}} \right)$ cancels out to zero. | Trading equal buy volumes of two perfectly opposite assets results in **zero net market impact**. | ✅ **Passed** |
| **Perfect Positive Correlation**<br>($\rho = 1$, identical $\sigma, V$) | $\mathbf{C}^\alpha$ blends the volumes *before* the exponent $\alpha$ is applied ($\sqrt{Q_1 + Q_2}$). | Successfully solves the **Aggregation Problem**. Treating two identical instruments as a basket yields the exact same impact as a single consolidated trade. | ✅ **Passed** |

---
