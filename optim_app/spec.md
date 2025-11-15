Create in ETPHQ folder a streamlit app with 2 tabs

First tab lets user

    load a csv or parquet file with marketId (string) and delta (float) columns

    display the content in a table that has 3 columns marketId, delta, solution

    let the user define 2 constants c and max_pos in the left pane

    display a solve button in the left pane

    once the solve button is pressed, the following optimisation problem is solved using cvxpy

    min c * sum_i |dw_i|
    dw_i = w_i - w_i^0
    |w_i| <= max_pos
    sum w_i = 0

    where w_i^0 are the values loaded from the file

    Add a generate data button to let the user generate random data for testing

On the second tab
 let the user load a barra exposure csv or parquet with one row per marketId and one column per factor

display the corresponding table

Add a button generate random data for testing

