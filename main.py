import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Lucrum",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Styling
st.markdown("""
<style>
    /* Main content styling */
    .main {
        padding: 2rem;
    }
    
    /* Card-like containers */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Headers styling */
    .main .block-container h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* Metric value colors */
    .metric-value {
        color: #2ecc71;
    }
    .metric-negative {
        color: #e74c3c;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding: 2rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Drop existing budgets table
    c.execute('DROP TABLE IF EXISTS budgets')
    
    # Create updated budgets table
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        period TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, category, period, start_date)
    )''')
    
    conn.commit()
    conn.close()

# Call init_db() to update the database structure
init_db()

# Initialize database
init_db()

# Initialize session state for user
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Login section
if st.session_state.user_id is None:
    # Custom CSS for login/register pages
    st.markdown("""
        <style>
            /* Main container styling */
            .auth-container {
                max-width: 400px;
                margin: 2rem auto;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            /* Form title */
            .form-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #00ff9d;
                text-align: center;
                margin-bottom: 2rem;
                letter-spacing: 0.1em;
            }
            
            /* Input fields */
            .stTextInput input, .stPasswordInput input {
                background: rgba(255, 255, 255, 0.08) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 8px !important;
                color: white !important;
                padding: 1rem !important;
                font-size: 1rem !important;
            }
            
            .stTextInput input:focus, .stPasswordInput input:focus {
                border-color: #00ff9d !important;
                box-shadow: 0 0 0 2px rgba(0, 255, 157, 0.2) !important;
            }
            
            /* Submit button */
            .stButton button {
                background: #00ff9d !important;
                color: black !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 0.75rem 2rem !important;
                font-size: 1.1rem !important;
                font-weight: 600 !important;
                width: 100% !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton button:hover {
                background: #00cc7d !important;
                transform: translateY(-2px);
            }
            
            /* Toggle link */
            .toggle-link {
                text-align: center;
                color: #888888;
                margin-top: 1rem;
                font-size: 0.9rem;
            }
            
            .toggle-link a {
                color: #00ff9d;
                text-decoration: none;
                font-weight: 600;
            }
            
            .toggle-link a:hover {
                text-decoration: underline;
            }
            
            /* Error messages */
            .stAlert {
                background: rgba(255, 87, 87, 0.1) !important;
                border-color: #ff5757 !important;
                color: #ff5757 !important;
                border-radius: 8px !important;
            }
            
            /* Success messages */
            .element-container div[data-testid="stMarkdownContainer"] div.success {
                background: rgba(0, 255, 157, 0.1) !important;
                border-color: #00ff9d !important;
                color: #00ff9d !important;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Login/Register toggle
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False

        if st.session_state.show_register:
            st.markdown('<h1 class="form-title">Create Account</h1>', unsafe_allow_html=True)
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Enter your username")
                new_password = st.text_input("Password", type="password", placeholder="Enter your password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                if st.form_submit_button("Register", use_container_width=True):
                    if new_password != confirm_password:
                        st.error("Passwords do not match!")
                    elif not new_username or not new_password:
                        st.error("Please fill in all fields!")
                    else:
                        conn = sqlite3.connect('finance.db')
                        c = conn.cursor()
                        try:
                            c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                                    (new_username, new_password))
                            conn.commit()
                            st.markdown('<div class="success">Registration successful! Please login.</div>', 
                                      unsafe_allow_html=True)
                            st.balloons()
                            st.session_state.show_register = False
                        except sqlite3.IntegrityError:
                            st.error("Username already exists!")
                        finally:
                            conn.close()
            
            st.markdown('<div class="toggle-link">Don\'t have an account?</div>', unsafe_allow_html=True)
            if st.button("Register here", key="reg_here"):
                st.session_state.show_register = True
                st.rerun()

        else:
            st.markdown('<h1 class="form-title">Welcome Back</h1>', unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if not username or not password:
                        st.error("Please fill in all fields!")
                    else:
                        conn = sqlite3.connect('finance.db')
                        c = conn.cursor()
                        c.execute('SELECT id FROM users WHERE username = ? AND password = ?',
                                (username, password))
                        result = c.fetchone()
                        conn.close()
                        
                        if result:
                            st.session_state.user_id = result[0]
                            st.rerun()
                        else:
                            st.error("Invalid username or password!")
            
            st.markdown('<div class="toggle-link">Don\'t have an account?</div>', unsafe_allow_html=True)
            if st.button("Register here", key="reg_here"):
                st.session_state.show_register = True
                st.rerun()

# Database functions remain the same as previous version

# Add new function to get username
def get_username(user_id):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Add function to delete transaction
def delete_transaction(transaction_id):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

# Add function to update transaction
def update_transaction(id, date, type_, amount, category):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('''UPDATE transactions 
                 SET date = ?, type = ?, amount = ?, category = ?
                 WHERE id = ?''', (date, type_, amount, category, id))
    conn.commit()
    conn.close()

def get_transactions(user_id):
    conn = sqlite3.connect('finance.db')
    df = pd.read_sql_query('''
        SELECT id, date, type, amount, category, description 
        FROM transactions 
        WHERE user_id = ?
        ORDER BY date DESC''', 
        conn, 
        params=(user_id,))
    conn.close()
    return df

def add_transaction(user_id, date, type_, amount, category, description):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO transactions (user_id, date, type, amount, category, description)
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (user_id, date, type_, amount, category, description))
    conn.commit()
    conn.close()

def set_budget(user_id, category, amount, period):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Calculate start and end dates based on period
    today = datetime.now()
    if period == "Weekly":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "Monthly":
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month.replace(day=1) - timedelta(days=1)
    else:  # Yearly
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    
    c.execute('''INSERT OR REPLACE INTO budgets 
                 (user_id, category, amount, period, start_date, end_date)
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (user_id, category, amount, period, 
               start_date.strftime("%Y-%m-%d"), 
               end_date.strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_budgets(user_id, period=None):
    conn = sqlite3.connect('finance.db')
    query = '''
        SELECT category, amount, period, start_date, end_date
        FROM budgets
        WHERE user_id = ?
    '''
    params = [user_id]
    
    if period:
        query += ' AND period = ?'
        params.append(period)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Add debt management functions
def add_debt(user_id, name, type_, amount, interest_rate, minimum_payment, due_date):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO debts (user_id, name, type, amount, interest_rate, 
                minimum_payment, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')''', 
              (user_id, name, type_, amount, interest_rate, minimum_payment, due_date))
    conn.commit()
    conn.close()

def get_debts(user_id):
    conn = sqlite3.connect('finance.db')
    df = pd.read_sql_query('''
        SELECT * FROM debts 
        WHERE user_id = ? AND status = 'Active'
        ORDER BY due_date''', 
        conn, params=(user_id,))
    conn.close()
    return df

def update_debt(debt_id, amount):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('UPDATE debts SET amount = ? WHERE id = ?', (amount, debt_id))
    conn.commit()
    conn.close()

def mark_debt_paid(debt_id):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Get debt details before marking as paid
    c.execute("SELECT name, amount FROM debts WHERE id = ?", (debt_id,))
    debt_details = c.fetchone()
    
    if debt_details:
        # Update debt status
        c.execute("UPDATE debts SET status = 'Paid' WHERE id = ?", (debt_id,))
        
        # Add as expense transaction
        c.execute('''INSERT INTO transactions 
                    (user_id, date, type, amount, category, description)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (st.session_state.user_id, 
                  datetime.now().strftime("%Y-%m-%d"),
                  "Expense",
                  debt_details[1],
                  "Debt Payment",
                  f"Paid off: {debt_details[0]}")
        )
    
    conn.commit()
    conn.close()

# Add bill reminder functions
def add_bill_reminder(user_id, name, amount, due_date, frequency):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO bill_reminders 
                 (user_id, name, amount, due_date, frequency, status)
                 VALUES (?, ?, ?, ?, ?, 'Pending')''',
              (user_id, name, amount, due_date, frequency))
    conn.commit()
    conn.close()

def get_bill_reminders(user_id):
    conn = sqlite3.connect('finance.db')
    df = pd.read_sql_query('''
        SELECT * FROM bill_reminders 
        WHERE user_id = ? AND status = 'Pending'
        ORDER BY due_date''',
        conn, params=(user_id,))
    conn.close()
    return df

def mark_bill_paid(reminder_id):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Get bill details before marking as paid
    c.execute("SELECT name, amount FROM bill_reminders WHERE id = ?", (reminder_id,))
    bill_details = c.fetchone()
    
    if bill_details:
        # Update bill status
        c.execute("UPDATE bill_reminders SET status = 'Paid' WHERE id = ?", (reminder_id,))
        
        # Add as expense transaction
        c.execute('''INSERT INTO transactions 
                    (user_id, date, type, amount, category, description)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (st.session_state.user_id, 
                  datetime.now().strftime("%Y-%m-%d"),
                  "Expense",
                  bill_details[1],
                  "Bills",
                  f"Paid: {bill_details[0]}")
        )
    
    conn.commit()
    conn.close()

def update_bill_reminder(reminder_id, name, amount, due_date, frequency):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('''UPDATE bill_reminders 
                 SET name = ?, amount = ?, due_date = ?, frequency = ?
                 WHERE id = ?''', 
              (name, amount, due_date, frequency, reminder_id))
    conn.commit()
    conn.close()

def display_transaction(transaction):
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        
        # Date and type with icon
        with col1:
            icon = "📈" if transaction['type'] == "Income" else "📉"
            st.write(f"{icon} {transaction['date'].strftime('%Y-%m-%d')}")
        
        # Description and category
        with col2:
            st.write(f"**{transaction['category']}**")
            if pd.notna(transaction['description']) and transaction['description']:
                st.write(f"_{transaction['description']}_")
        
        # Amount with color
        with col3:
            amount_color = "#2ecc71" if transaction['type'] == "Income" else "#e74c3c"
            st.markdown(f"<h3 style='color: {amount_color}'>${transaction['amount']:,.2f}</h3>", 
                       unsafe_allow_html=True)
        
        # Actions
        with col4:
            if st.button("Edit", key=f"edit_{transaction['id']}"):
                st.session_state.editing = transaction['id']
            if st.button("Delete", key=f"delete_{transaction['id']}"):
                delete_transaction(transaction['id'])
                st.success("Transaction deleted!")
                st.rerun()
        
        # Edit form
        if hasattr(st.session_state, 'editing') and st.session_state.editing == transaction['id']:
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    edit_date = st.date_input(
                        "Date", 
                        value=pd.to_datetime(transaction['date']).date(),
                        key=f"edit_date_{transaction['id']}"
                    )
                    edit_type = st.selectbox(
                        "Type",
                        ["Income", "Expense"],
                        index=0 if transaction['type'] == "Income" else 1,
                        key=f"edit_type_{transaction['id']}"
                    )
                with col2:
                    edit_amount = st.number_input(
                        "Amount",
                        value=float(transaction['amount']),
                        min_value=0.0,
                        key=f"edit_amount_{transaction['id']}"
                    )
                    edit_category = st.selectbox(
                        "Category",
                        income_categories if edit_type == "Income" else expense_categories,
                        index=(income_categories if edit_type == "Income" else expense_categories).index(transaction['category']),
                        key=f"edit_category_{transaction['id']}"
                    )
                
                if st.button("Save Changes", key=f"save_{transaction['id']}"):
                    update_transaction(
                        transaction['id'],
                        edit_date.strftime("%Y-%m-%d"),
                        edit_type,
                        edit_amount,
                        edit_category
                    )
                    del st.session_state.editing
                    st.success("Transaction updated!")
                    st.rerun()
        
        st.divider()

def create_metric_card(title, value, delta=None, icon="💰"):
    st.markdown(f"""
        <div style="
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0; color: #666;">{icon} {title}</h3>
            <h2 style="margin: 0.5rem 0; color: #1f77b4;">${value:,.2f}</h2>
            {f'<p style="margin: 0; color: {"#2ecc71" if delta >= 0 else "#e74c3c"}">{"↑" if delta >= 0 else "↓"} {abs(delta):,.2f}%</p>' if delta is not None else ''}
        </div>
    """, unsafe_allow_html=True)

def create_budget_progress(category, spent, budget):
    progress = (spent / budget) * 100 if budget > 0 else 0
    color = "#2ecc71" if progress <= 75 else "#f1c40f" if progress <= 90 else "#e74c3c"
    
    st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>{category}</span>
                <span>${spent:,.2f} / ${budget:,.2f}</span>
            </div>
            <div style="
                width: 100%;
                height: 10px;
                background-color: #f0f2f6;
                border-radius: 5px;
                overflow: hidden;
            ">
                <div style="
                    width: {min(progress, 100)}%;
                    height: 100%;
                    background-color: {color};
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Main interface (login part remains the same)
if st.session_state.user_id is None:
    # ... (keep existing login code)
    pass
else:
    # Get username for display
    username = get_username(st.session_state.user_id)
    
    # Main app header with user info
    st.title(f"Welcome {username}! 👋")
    
    # Sidebar for adding transactions
    with st.sidebar:
        st.header("Add Transaction")
        date = st.date_input("Date", datetime.now())
        transaction_type = st.selectbox("Type", ["Income", "Expense"])
        description = st.text_input("Description", placeholder="Enter transaction description")
        
        # Dynamic categories based on type
        income_categories = ["Salary", "Investment", "Side Hustle", "Allowance", "Other Income"]
        expense_categories = ["Food", "Transport", "Education", "Entertainment", "Shopping", 
                            "Bills", "Healthcare", "Housing", "Other Expenses"]
        
        category = st.selectbox(
            "Category",
            income_categories if transaction_type == "Income" else expense_categories
        )
        
        amount = st.number_input("Amount", min_value=0.0, value=0.0, step=0.01)
        
        if st.button("Add Transaction", type="primary"):
            if amount > 0:
                with st.spinner('Adding transaction...'):
                    add_transaction(
                        st.session_state.user_id,
                        date.strftime("%Y-%m-%d"),
                        transaction_type,
                        amount,
                        category,
                        description
                    )
                st.success("Transaction added!")
                st.balloons()  # Celebration effect!
                st.rerun()
            else:
                st.error("Please enter an amount greater than 0")
        
        if st.button("Logout", type="secondary"):
            st.session_state.user_id = None
            st.rerun()

    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "📝 Transactions", "📈 Analysis", 
        "💰 Budget", "🤖 RAO Bot", "💳 Debt Tracker", "📅 Bills"])

    # Get all transactions
    df = get_transactions(st.session_state.user_id)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])

    with tab1:
        with st.spinner('Loading your financial summary...'):
            # Get transactions
            if not df.empty:
                # Get budgets data
                budgets_df = get_budgets(st.session_state.user_id)
                
                total_income = df[df['type'] == 'Income']['amount'].sum()
                total_expense = df[df['type'] == 'Expense']['amount'].sum()
                balance = total_income - total_expense

                col1, col2, col3 = st.columns(3)
                with col1:
                    create_metric_card("Total Income", total_income, None, "💵")
                with col2:
                    create_metric_card("Total Expenses", total_expense, None, "💸")
                with col3:
                    create_metric_card("Current Balance", balance, None, "🏦")

                # Time period selector for overview
                period = st.selectbox(
                    "Select Time Period",
                    ["Last 7 days", "Last 30 days", "This Month", "This Year", "All Time"]
                )

                # Filter data based on selected period
                today = datetime.now()
                if period == "Last 7 days":
                    df_period = df[df['date'] >= today - timedelta(days=7)]
                elif period == "Last 30 days":
                    df_period = df[df['date'] >= today - timedelta(days=30)]
                elif period == "This Month":
                    df_period = df[df['date'].dt.month == today.month]
                elif period == "This Year":
                    df_period = df[df['date'].dt.year == today.year]
                else:
                    df_period = df

                # Show charts for the selected period
                col1, col2 = st.columns(2)
                with col1:
                    # Expense breakdown
                    expenses = df_period[df_period['type'] == 'Expense']
                    if not expenses.empty:
                        fig = px.pie(expenses, values='amount', names='category',
                                   title=f"Expense Distribution - {period}")
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Income breakdown
                    income = df_period[df_period['type'] == 'Income']
                    if not income.empty:
                        fig = px.pie(income, values='amount', names='category',
                                   title=f"Income Distribution - {period}")
                        st.plotly_chart(fig, use_container_width=True)

                # Show budget progress
                if not df.empty:
                    st.subheader("Budget Progress")
                    
                    if not budgets_df.empty:
                        # Calculate current month's expenses by category
                        current_month_expenses = df[
                            (df['type'] == 'Expense') & 
                            (df['date'].dt.month == datetime.now().month)
                        ].groupby('category')['amount'].sum()
                        
                        # Show progress bars for each category
                        for _, budget_row in budgets_df.iterrows():
                            category = budget_row['category']
                            budget_amount = budget_row['amount']
                            spent = current_month_expenses.get(category, 0)
                            create_budget_progress(category, spent, budget_amount)

                        # Add budget alerts
                        st.subheader("Budget Alerts")
                        for _, budget_row in budgets_df.iterrows():
                            category = budget_row['category']
                            budget_amount = budget_row['amount']
                            spent = current_month_expenses.get(category, 0)
                            progress = (spent / budget_amount) * 100 if budget_amount > 0 else 0
                            
                            if progress >= 90:
                                st.error(f"⚠️ {category}: You've used {progress:.1f}% of your budget!")
                            elif progress >= 75:
                                st.warning(f"⚠️ {category}: You've used {progress:.1f}% of your budget")

    with tab2:
        with st.spinner('Loading your transactions...'):
            # Transaction management
            st.header("Manage Transactions")
            
            # Search and filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                search_term = st.text_input("Search by category")
            with col2:
                type_filter = st.multiselect("Filter by type", ["Income", "Expense"])
            with col3:
                date_range = st.date_input("Date range", 
                                         value=(datetime.now() - timedelta(days=30), datetime.now()),
                                         key="date_range")

            if not df.empty:
                # Apply filters
                filtered_df = df.copy()
                if search_term:
                    filtered_df = filtered_df[filtered_df['category'].str.contains(search_term, case=False)]
                if type_filter:
                    filtered_df = filtered_df[filtered_df['type'].isin(type_filter)]
                if len(date_range) == 2:
                    filtered_df = filtered_df[
                        (filtered_df['date'].dt.date >= date_range[0]) & 
                        (filtered_df['date'].dt.date <= date_range[1])
                    ]

                # Display transactions using the new function
                for _, transaction in filtered_df.iterrows():
                    display_transaction(transaction)

    with tab3:
        with st.spinner('Analyzing your financial data...'):
            st.header("Financial Analysis")
            
            if not df.empty:
                # Spending trends over time
                monthly_expenses = df[df['type'] == 'Expense'].set_index('date').resample('M')['amount'].sum()
                monthly_income = df[df['type'] == 'Income'].set_index('date').resample('M')['amount'].sum()
                
                fig = px.line(title="Monthly Trends")
                fig.add_scatter(x=monthly_expenses.index, y=monthly_expenses.values, name="Expenses")
                fig.add_scatter(x=monthly_income.index, y=monthly_income.values, name="Income")
                st.plotly_chart(fig, use_container_width=True)

                # Category analysis
                st.subheader("Top Spending Categories")
                top_expenses = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().sort_values(ascending=False)
                fig = px.bar(
                    data_frame=pd.DataFrame({'Category': top_expenses.index, 'Amount': top_expenses.values}),
                    x='Category',
                    y='Amount',
                    title="Top Spending Categories"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Basic statistics
                st.subheader("Statistics")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Average monthly expense:", f"${df[df['type'] == 'Expense'].groupby(df['date'].dt.month)['amount'].sum().mean():,.2f}")
                with col2:
                    st.write("Average monthly income:", f"${df[df['type'] == 'Income'].groupby(df['date'].dt.month)['amount'].sum().mean():,.2f}")
            else:
                st.info("Add some transactions to see your financial analysis!")

    with tab4:
        with st.spinner('Loading budget information...'):
            st.header("Budget Management")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                budget_period = st.selectbox(
                    "Budget Period",
                    ["Monthly", "Weekly", "Yearly"],
                    key="budget_period"
                )
            with col2:
                if st.button("Confirm Period", type="primary"):
                    st.session_state.confirmed_period = budget_period
                    st.rerun()
            
            if 'confirmed_period' not in st.session_state:
                st.session_state.confirmed_period = "Monthly"  # Default period
            
            # Get existing budgets for the selected period
            budgets_df = get_budgets(st.session_state.user_id, st.session_state.confirmed_period)
            
            # Show current period info
            if st.session_state.confirmed_period == "Weekly":
                start_date = datetime.now() - timedelta(days=datetime.now().weekday())
                end_date = start_date + timedelta(days=6)
            elif st.session_state.confirmed_period == "Monthly":
                start_date = datetime.now().replace(day=1)
                next_month = datetime.now().replace(day=28) + timedelta(days=4)
                end_date = next_month.replace(day=1) - timedelta(days=1)
            else:  # Yearly
                start_date = datetime.now().replace(month=1, day=1)
                end_date = datetime.now().replace(month=12, day=31)
            
            st.info(f"Showing budgets for: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Show budget progress
            if not df.empty:
                st.subheader("Budget Progress")
                
                if not budgets_df.empty:
                    # Calculate current month's expenses by category
                    current_month_expenses = df[
                        (df['type'] == 'Expense') & 
                        (df['date'].dt.month == datetime.now().month)
                    ].groupby('category')['amount'].sum()
                    
                    # Show progress bars for each category
                    for _, budget_row in budgets_df.iterrows():
                        category = budget_row['category']
                        budget_amount = budget_row['amount']
                        spent = current_month_expenses.get(category, 0)
                        create_budget_progress(category, spent, budget_amount)

                    # Add budget alerts
                    st.subheader("Budget Alerts")
                    for _, budget_row in budgets_df.iterrows():
                        category = budget_row['category']
                        budget_amount = budget_row['amount']
                        spent = current_month_expenses.get(category, 0)
                        progress = (spent / budget_amount) * 100 if budget_amount > 0 else 0
                        
                        if progress >= 90:
                            st.error(f"⚠️ {category}: You've used {progress:.1f}% of your budget!")
                        elif progress >= 75:
                            st.warning(f"⚠️ {category}: You've used {progress:.1f}% of your budget")
                
            # Create budget settings for each expense category
            st.subheader("Set Budget Limits by Category")
            
            # Initialize session state for budget values if not exists
            if 'budget_values' not in st.session_state:
                st.session_state.budget_values = {}
            
            for category in expense_categories:
                current_budget = budgets_df[budgets_df['category'] == category]['amount'].iloc[0] if not budgets_df.empty and (budgets_df['category'] == category).any() else 0.0
                
                # Initialize session state for this category if not exists
                if category not in st.session_state.budget_values:
                    st.session_state.budget_values[category] = current_budget
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(category)
                with col2:
                    new_budget = st.number_input(
                        f"Budget for {category}",
                        min_value=0.0,
                        value=float(st.session_state.budget_values[category]),
                        step=10.0,
                        key=f"budget_input_{category}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Only show confirm button if value has changed
                    if new_budget != current_budget:
                        if st.button("Confirm", key=f"confirm_{category}"):
                            set_budget(st.session_state.user_id, category, new_budget, budget_period)
                            st.session_state.budget_values[category] = new_budget
                            st.success(f"Budget updated for {category}")
                            st.rerun()
                    else:
                        st.write("") # Empty space for alignment

    with tab5:
        st.header("Financial AI Assistant")
        
        if not df.empty:
            # Common financial questions
            question = st.selectbox(
                "What would you like to know?",
                [
                    "How are my spending habits?",
                    "Where can I potentially save money?",
                    "Am I on track with my budgets?",
                    "What are my highest expenses?",
                    "How is my income-expense ratio?",
                ]
            )
            
            
            if st.button("Get Insights"):
                with st.spinner("Analyzing your financial data..."):
                    # Calculate key metrics
                    monthly_expenses = df[df['type'] == 'Expense'].groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum()
                    avg_monthly_expense = monthly_expenses.mean()
                    top_expenses = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().sort_values(ascending=False)
                    income_expense_ratio = df[df['type'] == 'Income']['amount'].sum() / df[df['type'] == 'Expense']['amount'].sum()
                    
                    # Get budget information
                    budgets_df = get_budgets(st.session_state.user_id)
                    current_month_expenses = df[
                        (df['type'] == 'Expense') & 
                        (df['date'].dt.month == datetime.now().month)
                    ].groupby('category')['amount'].sum()
                    
                    st.write("🤖 Here's my analysis:")
                    
                    if question == "How are my spending habits?":
                        st.write(f"📊 Your average monthly spending is ${avg_monthly_expense:,.2f}")
                        if monthly_expenses.iloc[-1] > avg_monthly_expense:
                            st.warning("⚠️ Your spending this month is above your monthly average.")
                        else:
                            st.success("✅ Your spending this month is below your monthly average.")
                        
                        # Show spending trend
                        fig = px.line(title="Monthly Spending Trend")
                        fig.add_scatter(x=monthly_expenses.index, y=monthly_expenses.values)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif question == "Where can I potentially save money?":
                        st.write("💡 Here are some observations:")
                        
                        # Identify categories with highest spending
                        top_3_expenses = top_expenses.head(3)
                        st.write("Your top 3 expense categories are:")
                        for category, amount in top_3_expenses.items():
                            st.write(f"- {category}: ${amount:,.2f}")
                        
                        # Look for unusual spikes in spending
                        recent_expenses = df[
                            (df['type'] == 'Expense') & 
                            (df['date'] >= datetime.now() - timedelta(days=30))
                        ]
                        if not recent_expenses.empty:
                            unusual_expenses = recent_expenses[recent_expenses['amount'] > recent_expenses['amount'].mean() * 1.5]
                            if not unusual_expenses.empty:
                                st.write("\n🔍 I noticed some unusually large expenses recently:")
                                for _, expense in unusual_expenses.iterrows():
                                    st.write(f"- ${expense['amount']:,.2f} on {expense['category']} ({expense['date'].strftime('%Y-%m-%d')})")
                    
                    elif question == "Am I on track with my budgets?":
                        if not budgets_df.empty:
                            st.write("🎯 Budget Progress Analysis:")
                            for _, budget_row in budgets_df.iterrows():
                                category = budget_row['category']
                                budget_amount = budget_row['amount']
                                spent = current_month_expenses.get(category, 0)
                                progress = (spent / budget_amount) * 100 if budget_amount > 0 else 0
                                
                                if progress >= 90:
                                    st.error(f"⚠️ {category}: You've used {progress:.1f}% of your budget!")
                                elif progress >= 75:
                                    st.warning(f"⚠️ {category}: You've used {progress:.1f}% of your budget")
                                else:
                                    st.success(f"✅ {category}: You've used {progress:.1f}% of your budget")
                        else:
                            st.info("You haven't set any budgets yet. Set them in the Budget tab!")
                    
                    elif question == "What are my highest expenses?":
                        st.write("💰 Here are your top expenses:")
                        fig = px.bar(
                            x=top_expenses.head(5).index,
                            y=top_expenses.head(5).values,
                            title="Top 5 Expense Categories"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Provide specific insights
                        st.write("\n📝 Key observations:")
                        for category, amount in top_expenses.head(5).items():
                            percentage = (amount / top_expenses.sum()) * 100
                            st.write(f"- {category}: ${amount:,.2f} ({percentage:.1f}% of total expenses)")
                    
                    elif question == "How is my income-expense ratio?":
                        st.write(f"📊 Your income-expense ratio is {income_expense_ratio:.2f}")
                        if income_expense_ratio < 1:
                            st.error("⚠️ You're spending more than you're earning!")
                        elif income_expense_ratio < 1.2:
                            st.warning("⚠️ Your spending is close to your income. Consider saving more!")
                        else:
                            st.success("✅ You're earning more than you're spending - great job!")
                        
                        # Show monthly comparison
                        monthly_comparison = pd.DataFrame({
                            'Income': df[df['type'] == 'Income'].groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum(),
                            'Expenses': df[df['type'] == 'Expense'].groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum()
                        })
                        fig = px.bar(monthly_comparison, barmode='group', title="Monthly Income vs Expenses")
                        st.plotly_chart(fig, use_container_width=True)
                    
        else:
            st.info("Add some transactions to get personalized insights!")

    with tab6:
        st.header("Debt Tracker")
        
        # Add new debt section
        with st.expander("Add New Debt", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                debt_name = st.text_input("Debt Name", placeholder="e.g., Car Loan, Credit Card")
                debt_type = st.selectbox("Type", [
                    "Credit Card", "Student Loan", "Personal Loan", 
                    "Mortgage", "Auto Loan", "Medical Debt", "Other"
                ])
                amount = st.number_input("Total Amount", min_value=0.0, step=100.0)
            with col2:
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
                minimum_payment = st.number_input("Minimum Monthly Payment", min_value=0.0, step=10.0)
                due_date = st.date_input("Next Due Date")
                
            if st.button("Add Debt", type="primary"):
                if debt_name and amount > 0:
                    add_debt(
                        st.session_state.user_id,
                        debt_name,
                        debt_type,
                        amount,
                        interest_rate,
                        minimum_payment,
                        due_date.strftime("%Y-%m-%d")
                    )
                    st.success("Debt added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")
        
        # Display existing debts
        debts_df = get_debts(st.session_state.user_id)
        if not debts_df.empty:
            st.subheader("Your Debts")
            
            # Summary metrics
            total_debt = debts_df['amount'].sum()
            total_monthly_payments = debts_df['minimum_payment'].sum()
            weighted_avg_interest = (debts_df['amount'] * debts_df['interest_rate']).sum() / total_debt
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Debt", f"${total_debt:,.2f}")
            col2.metric("Monthly Payments", f"${total_monthly_payments:,.2f}")
            col3.metric("Avg Interest Rate", f"{weighted_avg_interest:.1f}%")
            
            # Debt breakdown visualization
            st.subheader("Debt Breakdown")
            fig = px.pie(debts_df, values='amount', names='type', 
                        title="Debt Distribution by Type")
            st.plotly_chart(fig, use_container_width=True)
            
            # List all debts with progress tracking
            st.subheader("Debt Details")
            for _, debt in debts_df.iterrows():
                with st.container():
                    cols = st.columns([3, 2, 2, 1])
                    
                    cols[0].write(f"**{debt['name']}** ({debt['type']})")
                    cols[0].write(f"Amount: ${debt['amount']:,.2f}")
                    
                    cols[1].write("Interest Rate")
                    cols[1].write(f"{debt['interest_rate']}%")
                    
                    cols[2].write("Next Due Date")
                    due_date = pd.to_datetime(debt['due_date']).date()
                    days_until_due = (due_date - datetime.now().date()).days
                    if days_until_due <= 7:
                        cols[2].error(f"{days_until_due} days left")
                    else:
                        cols[2].write(f"{days_until_due} days left")
                    
                    update_col = cols[3]
                    if update_col.button("Update", key=f"update_debt_{debt['id']}"):
                        st.session_state.editing_debt = debt['id']
                    if update_col.button("Paid", key=f"paid_debt_{debt['id']}"):
                        mark_debt_paid(debt['id'])
                        st.success("Debt marked as paid and added to transactions!")
                        st.rerun()
                    
                    if hasattr(st.session_state, 'editing_debt') and st.session_state.editing_debt == debt['id']:
                        new_amount = st.number_input(
                            "Current Amount",
                            value=float(debt['amount']),
                            min_value=0.0,
                            step=10.0
                        )
                        if st.button("Save Changes"):
                            update_debt(debt['id'], new_amount)
                            del st.session_state.editing_debt
                            st.success("Debt updated!")
                            st.rerun()
                    
                    st.divider()
            
            # Debt payoff projections
            st.subheader("Debt Payoff Projections")
            months_to_payoff = total_debt / total_monthly_payments
            interest_paid = (total_debt * weighted_avg_interest/100 * months_to_payoff/12)
            
            col1, col2 = st.columns(2)
            col1.metric("Estimated Months to Payoff", f"{months_to_payoff:.1f} months")
            col2.metric("Estimated Interest to be Paid", f"${interest_paid:,.2f}")
            
        else:
            st.info("You haven't added any debts yet. Add one above to start tracking!")

    with tab7:
        st.header("Bill Reminders")
        
        # Add new bill reminder section
        with st.expander("Add New Bill Reminder", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                bill_name = st.text_input("Bill Name", placeholder="e.g., Electricity, Internet")
                bill_amount = st.number_input("Amount", min_value=0.0, step=1.0)
            with col2:
                due_date = st.date_input("Due Date")
                frequency = st.selectbox(
                    "Frequency",
                    ["Monthly", "Weekly", "Quarterly", "Annually", "One-time"]
                )
            
            if st.button("Add Bill Reminder", type="primary"):
                if bill_name and bill_amount > 0:
                    add_bill_reminder(
                        st.session_state.user_id,
                        bill_name,
                        bill_amount,
                        due_date.strftime("%Y-%m-%d"),
                        frequency
                    )
                    st.success("Bill reminder added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")
        
        # Display existing bill reminders
        reminders_df = get_bill_reminders(st.session_state.user_id)
        if not reminders_df.empty:
            # Summary metrics
            total_bills = reminders_df['amount'].sum()
            upcoming_bills = reminders_df[
                pd.to_datetime(reminders_df['due_date']) <= datetime.now() + timedelta(days=7)
            ]
            
            col1, col2 = st.columns(2)
            col1.metric("Total Upcoming Bills", f"${total_bills:,.2f}")
            col2.metric("Due This Week", len(upcoming_bills))
            
            # List all bill reminders
            st.subheader("Upcoming Bills")
            for _, reminder in reminders_df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{reminder['name']}**")
                        st.write(f"Amount: ${reminder['amount']:,.2f}")
                    
                    with col2:
                        st.write("Frequency")
                        st.write(reminder['frequency'])
                    
                    with col3:
                        st.write("Due Date")
                        due_date = pd.to_datetime(reminder['due_date']).date()
                        days_until_due = (due_date - datetime.now().date()).days
                        if days_until_due <= 3:
                            st.error(f"{days_until_due} days left")
                        elif days_until_due <= 7:
                            st.warning(f"{days_until_due} days left")
                        else:
                            st.write(f"{days_until_due} days left")
                    
                    with col4:
                        if st.button("Edit", key=f"edit_bill_{reminder['id']}"):
                            st.session_state.editing_bill = reminder['id']
                        if st.button("Paid", key=f"paid_bill_{reminder['id']}"):
                            mark_bill_paid(reminder['id'])
                            # Optionally add as transaction
                            add_transaction(
                                st.session_state.user_id,
                                datetime.now().strftime("%Y-%m-%d"),
                                "Expense",
                                reminder['amount'],
                                "Bills",
                                reminder['name']
                            )
                            st.success("Bill marked as paid and added to transactions!")
                            st.rerun()
                    
                    # Edit form
                    if hasattr(st.session_state, 'editing_bill') and st.session_state.editing_bill == reminder['id']:
                        with st.container():
                            col1, col2 = st.columns(2)
                            with col1:
                                new_name = st.text_input("Name", value=reminder['name'])
                                new_amount = st.number_input("Amount", value=float(reminder['amount']), min_value=0.0)
                            with col2:
                                new_due_date = st.date_input("Due Date", value=pd.to_datetime(reminder['due_date']))
                                new_frequency = st.selectbox(
                                    "Frequency",
                                    ["Monthly", "Weekly", "Quarterly", "Annually", "One-time"],
                                    index=["Monthly", "Weekly", "Quarterly", "Annually", "One-time"].index(reminder['frequency'])
                                )
                            
                            if st.button("Save Changes"):
                                update_bill_reminder(
                                    reminder['id'],
                                    new_name,
                                    new_amount,
                                    new_due_date.strftime("%Y-%m-%d"),
                                    new_frequency
                                )
                                del st.session_state.editing_bill
                                st.success("Bill reminder updated!")
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("You haven't added any bill reminders yet. Add one above to start tracking!")
