"""
Investment Analyzer Component
Comprehensive ROI analysis for Airbnb investment opportunities
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dashboard.utils.styling import create_roi_card


def investment_analyzer_page():
    """Investment analyzer page with comprehensive ROI calculations"""

    st.markdown(
        """
    <div class="custom-card">
        <h2>📊 Investment Analyzer</h2>
        <p>
            Evaluate investment opportunities with comprehensive ROI analysis,
            risk assessment, and sensitivity testing.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Check if data is loaded
    if not st.session_state.data_loaded:
        st.warning("Please wait for data to load on the home page first.")
        return

    data = st.session_state.data

    # Input Section
    st.markdown("### 📝 Investment Parameters")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Property Details")
        purchase_price = st.number_input(
            "Purchase Price ($)",
            min_value=50000,
            max_value=2000000,
            value=500000,
            step=10000,
            help="Total property purchase price",
        )

        renovation_cost = st.number_input(
            "Renovation/Setup Cost ($)",
            min_value=0,
            max_value=200000,
            value=25000,
            step=5000,
            help="Initial renovation and furnishing costs",
        )

        down_payment_pct = st.slider(
            "Down Payment (%)",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            help="Percentage of purchase price paid upfront",
        )

        mortgage_rate = st.slider(
            "Mortgage Interest Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=6.5,
            step=0.25,
            help="Annual mortgage interest rate",
        )

    with col2:
        st.markdown("#### Rental Assumptions")

        nightly_rate = st.number_input(
            "Expected Nightly Rate ($)",
            min_value=50,
            max_value=1000,
            value=150,
            step=10,
            help="Average nightly rate (use Price Predictor for estimates)",
        )

        occupancy_rate = st.slider(
            "Occupancy Rate (%)",
            min_value=0,
            max_value=100,
            value=65,
            step=5,
            help="Percentage of nights booked per year",
        )

        cleaning_fee = st.number_input(
            "Cleaning Fee per Booking ($)",
            min_value=0,
            max_value=200,
            value=75,
            step=5,
        )

        avg_stay_length = st.slider(
            "Average Stay Length (nights)",
            min_value=1,
            max_value=14,
            value=3,
            step=1,
        )

    # Operating Expenses
    with st.expander("⚙️ Operating Expenses", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            property_tax_annual = st.number_input(
                "Property Tax ($/year)",
                min_value=0,
                max_value=50000,
                value=int(purchase_price * 0.01),
                step=500,
            )

            hoa_monthly = st.number_input(
                "HOA/Condo Fees ($/month)",
                min_value=0,
                max_value=1000,
                value=0,
                step=50,
            )

            utilities_monthly = st.number_input(
                "Utilities ($/month)",
                min_value=0,
                max_value=500,
                value=150,
                step=25,
            )

        with col2:
            insurance_annual = st.number_input(
                "Insurance ($/year)",
                min_value=0,
                max_value=10000,
                value=1500,
                step=100,
            )

            maintenance_pct = st.slider(
                "Maintenance Reserve (% of revenue)",
                min_value=0,
                max_value=20,
                value=10,
                step=1,
            )

            management_pct = st.slider(
                "Property Management Fee (% of revenue)",
                min_value=0,
                max_value=30,
                value=15,
                step=5,
            )

    # Calculate Button
    if st.button("📊 Calculate ROI", type="primary"):
        # Calculations
        down_payment = purchase_price * (down_payment_pct / 100)
        loan_amount = purchase_price - down_payment
        total_investment = down_payment + renovation_cost

        # Monthly mortgage payment
        if loan_amount > 0 and mortgage_rate > 0:
            monthly_rate = (mortgage_rate / 100) / 12
            num_payments = 30 * 12  # 30-year mortgage
            monthly_mortgage = (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** num_payments)
                / ((1 + monthly_rate) ** num_payments - 1)
            )
        else:
            monthly_mortgage = 0

        # Revenue calculations
        nights_booked = 365 * (occupancy_rate / 100)
        bookings_per_year = nights_booked / avg_stay_length

        annual_rental_revenue = nightly_rate * nights_booked
        annual_cleaning_revenue = cleaning_fee * bookings_per_year
        total_annual_revenue = annual_rental_revenue + annual_cleaning_revenue

        # Expense calculations
        annual_mortgage = monthly_mortgage * 12
        annual_hoa = hoa_monthly * 12
        annual_utilities = utilities_monthly * 12
        annual_maintenance = total_annual_revenue * (maintenance_pct / 100)
        annual_management = total_annual_revenue * (management_pct / 100)

        total_annual_expenses = (
            annual_mortgage
            + annual_hoa
            + annual_utilities
            + property_tax_annual
            + insurance_annual
            + annual_maintenance
            + annual_management
        )

        # Net income and ROI
        annual_net_income = total_annual_revenue - total_annual_expenses
        annual_cash_flow = annual_net_income  # Simplified

        if total_investment > 0:
            cash_on_cash_return = annual_cash_flow / total_investment
            cap_rate = annual_net_income / purchase_price
        else:
            cash_on_cash_return = 0
            cap_rate = 0

        # Results Display
        st.markdown("---")
        st.markdown("## 💰 Investment Analysis Results")

        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Cash-on-Cash Return",
                f"{cash_on_cash_return:.1%}",
                help="Annual cash flow divided by total cash invested",
            )

        with col2:
            st.metric(
                "Annual Cash Flow",
                f"${annual_cash_flow:,.0f}",
                help="Net income after all expenses",
            )

        with col3:
            st.metric(
                "Cap Rate",
                f"{cap_rate:.2%}",
                help="Net operating income divided by property value",
            )

        with col4:
            st.metric(
                "Monthly Cash Flow",
                f"${annual_cash_flow/12:,.0f}",
                help="Average monthly profit",
            )

        # ROI Card
        if cash_on_cash_return > 0.15:
            recommendation = "Strong Investment Opportunity"
        elif cash_on_cash_return > 0.08:
            recommendation = "Moderate Investment Potential"
        elif cash_on_cash_return > 0:
            recommendation = "Weak Investment Returns"
        else:
            recommendation = "Negative Cash Flow - Not Recommended"

        st.markdown(
            create_roi_card(cash_on_cash_return, recommendation),
            unsafe_allow_html=True,
        )

        # Detailed Breakdown
        st.markdown("### 📋 Financial Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💵 Revenue")
            revenue_data = {
                "Category": [
                    "Nightly Revenue",
                    "Cleaning Fees",
                    "**Total Revenue**",
                ],
                "Annual Amount": [
                    f"${annual_rental_revenue:,.0f}",
                    f"${annual_cleaning_revenue:,.0f}",
                    f"**${total_annual_revenue:,.0f}**",
                ],
                "Monthly Average": [
                    f"${annual_rental_revenue/12:,.0f}",
                    f"${annual_cleaning_revenue/12:,.0f}",
                    f"**${total_annual_revenue/12:,.0f}**",
                ],
            }
            st.dataframe(
                pd.DataFrame(revenue_data), hide_index=True, use_container_width=True
            )

            st.markdown(f"- **Nights Booked**: {nights_booked:.0f} nights/year")
            st.markdown(f"- **Bookings**: {bookings_per_year:.0f} bookings/year")

        with col2:
            st.markdown("#### 💸 Expenses")
            expense_data = {
                "Category": [
                    "Mortgage Payment",
                    "Property Tax",
                    "Insurance",
                    "HOA/Condo Fees",
                    "Utilities",
                    "Maintenance Reserve",
                    "Management Fees",
                    "**Total Expenses**",
                ],
                "Annual Amount": [
                    f"${annual_mortgage:,.0f}",
                    f"${property_tax_annual:,.0f}",
                    f"${insurance_annual:,.0f}",
                    f"${annual_hoa:,.0f}",
                    f"${annual_utilities:,.0f}",
                    f"${annual_maintenance:,.0f}",
                    f"${annual_management:,.0f}",
                    f"**${total_annual_expenses:,.0f}**",
                ],
                "Monthly Average": [
                    f"${annual_mortgage/12:,.0f}",
                    f"${property_tax_annual/12:,.0f}",
                    f"${insurance_annual/12:,.0f}",
                    f"${annual_hoa/12:,.0f}",
                    f"${annual_utilities/12:,.0f}",
                    f"${annual_maintenance/12:,.0f}",
                    f"${annual_management/12:,.0f}",
                    f"**${total_annual_expenses/12:,.0f}**",
                ],
            }
            st.dataframe(
                pd.DataFrame(expense_data), hide_index=True, use_container_width=True
            )

        # Sensitivity Analysis
        st.markdown("### 📊 Sensitivity Analysis")
        st.markdown(
            "See how changes in occupancy rate and nightly rate affect your ROI:"
        )

        # Create sensitivity matrix
        occupancy_range = np.arange(40, 91, 10)
        rate_range = np.arange(int(nightly_rate * 0.8), int(nightly_rate * 1.3), 20)

        sensitivity_data = []
        for occ in occupancy_range:
            row = []
            for rate in rate_range:
                nights = 365 * (occ / 100)
                bookings = nights / avg_stay_length
                revenue = (rate * nights) + (cleaning_fee * bookings)
                maint = revenue * (maintenance_pct / 100)
                mgmt = revenue * (management_pct / 100)
                expenses = (
                    annual_mortgage
                    + annual_hoa
                    + annual_utilities
                    + property_tax_annual
                    + insurance_annual
                    + maint
                    + mgmt
                )
                net = revenue - expenses
                roi = (net / total_investment * 100) if total_investment > 0 else 0
                row.append(roi)
            sensitivity_data.append(row)

        # Plot heatmap
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(sensitivity_data, cmap="RdYlGn", aspect="auto")

        ax.set_xticks(np.arange(len(rate_range)))
        ax.set_yticks(np.arange(len(occupancy_range)))
        ax.set_xticklabels([f"${r}" for r in rate_range])
        ax.set_yticklabels([f"{o}%" for o in occupancy_range])

        ax.set_xlabel("Nightly Rate", fontsize=12)
        ax.set_ylabel("Occupancy Rate", fontsize=12)
        ax.set_title("Cash-on-Cash Return (%)", fontsize=14, fontweight="bold")

        # Add text annotations
        for i in range(len(occupancy_range)):
            for j in range(len(rate_range)):
                text = ax.text(
                    j,
                    i,
                    f"{sensitivity_data[i][j]:.1f}%",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=9,
                )

        plt.colorbar(im, ax=ax, label="ROI (%)")
        plt.tight_layout()
        st.pyplot(fig)

        # Investment Summary
        st.markdown("### 💡 Investment Summary")

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:
            st.markdown(
                f"""
            **Initial Investment**
            - Purchase Price: ${purchase_price:,.0f}
            - Down Payment ({down_payment_pct}%): ${down_payment:,.0f}
            - Renovation: ${renovation_cost:,.0f}
            - **Total Cash Needed**: ${total_investment:,.0f}
            """
            )

        with summary_col2:
            st.markdown(
                f"""
            **Key Assumptions**
            - Nightly Rate: ${nightly_rate}
            - Occupancy: {occupancy_rate}%
            - Avg Stay: {avg_stay_length} nights
            - Management: {management_pct}% of revenue
            """
            )

        # Recommendations
        if cash_on_cash_return > 0.15:
            st.success(
                """
            ✅ **Strong Investment**: This property shows excellent return potential with a
            cash-on-cash return above 15%. Consider moving forward with due diligence.
            """
            )
        elif cash_on_cash_return > 0.08:
            st.warning(
                """
            ⚠️ **Moderate Investment**: Returns are positive but moderate. Consider negotiating
            a better purchase price or finding ways to increase revenue/reduce expenses.
            """
            )
        else:
            st.error(
                """
            ❌ **Weak/Negative Returns**: Current assumptions show poor returns. Consider
            passing on this opportunity or significantly adjusting your assumptions.
            """
            )

        st.info(
            """
        **💡 Tips for Improving ROI:**
        - Increase nightly rate through better amenities and photos
        - Improve occupancy through dynamic pricing and better marketing
        - Reduce management costs by self-managing
        - Negotiate lower purchase price or interest rate
        - Minimize renovation costs while maintaining quality
        """
        )
