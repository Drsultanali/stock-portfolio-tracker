import yfinance as yf
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os
class StockPortfolio:
    def __init__(self):
        self.portfolio = {}

    def add_stock(self, ticker, shares, buy_price=None):
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="1d")

        if stock_data.empty:
            print(f"${ticker}: No price data found. The stock might be delisted or the ticker is incorrect.")
            return

        current_price = stock_data['Close'].iloc[0]
        
        if buy_price is None:
            buy_price = current_price
        
        if ticker not in self.portfolio:
            self.portfolio[ticker] = {'shares': shares, 'buy_price': buy_price}
        else:
            self.portfolio[ticker]['shares'] += shares

        # Save the portfolio's total value after adding a stock
        self.save_portfolio_value()

    def remove_stock(self, ticker, shares):
        if ticker in self.portfolio:
            if self.portfolio[ticker]['shares'] > shares:
                self.portfolio[ticker]['shares'] -= shares
            elif self.portfolio[ticker]['shares'] == shares:
                del self.portfolio[ticker]
            else:
                print("You don't own that many shares")
        else:
            print(f"Stock {ticker} not in portfolio")

        # Save the portfolio's total value after removing a stock
        self.save_portfolio_value()

    def get_portfolio_value(self):
        total_value = 0
        for ticker, data in self.portfolio.items():
            stock = yf.Ticker(ticker)
            stock_data = stock.history(period="1d")

            if stock_data.empty:
                print(f"${ticker}: No price data found. Skipping.")
                continue

            current_price = stock_data['Close'].iloc[0]
            total_value += data['shares'] * current_price
        return total_value

    def get_gains_losses(self):
        gains_losses = {}
        for ticker, data in self.portfolio.items():
            stock = yf.Ticker(ticker)
            stock_data = stock.history(period="1d")

            if stock_data.empty:
                print(f"${ticker}: No price data found. Skipping.")
                continue

            current_price = stock_data['Close'].iloc[0]
            gain_loss = (current_price - data['buy_price']) * data['shares']
            gains_losses[ticker] = gain_loss
        return gains_losses

    def save_portfolio(self, filename='portfolio.json'):
        """Save the portfolio to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.portfolio, f)
        print(f"Portfolio saved to {filename}")

    def load_portfolio(self, filename='portfolio.json'):
        """Load the portfolio from a JSON file."""
        try:
            with open(filename, 'r') as f:
                self.portfolio = json.load(f)
            print(f"Portfolio loaded from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with an empty portfolio.")

    def save_portfolio_value(self, filename='portfolio_history.csv'):
        """Save the total portfolio value to a CSV file with a timestamp."""
        total_value = self.get_portfolio_value()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if the file exists
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            if not file_exists:
                # Write header if file does not exist
                csvwriter.writerow(['timestamp', 'total_value'])
            csvwriter.writerow([timestamp, total_value])

        print(f"Portfolio value of ${total_value:,.2f} saved at {timestamp}")


# Example usage
portfolio = StockPortfolio()

# Load the portfolio from file (if it exists)
portfolio.load_portfolio()

# Add some stocks
portfolio.add_stock('AAPL', 10, buy_price=150.00)
portfolio.add_stock('GOOGL', 5, buy_price=2700.00)

# Get portfolio value and gains/losses
print(f"Portfolio Value: ${portfolio.get_portfolio_value():,.2f}")
gains_losses = portfolio.get_gains_losses()
for ticker, gain_loss in gains_losses.items():
    print(f"{ticker}: ${gain_loss:,.2f} {'gain' if gain_loss >= 0 else 'loss'}")

# Save the portfolio to file
portfolio.save_portfolio()

def plot_portfolio_history(filename='portfolio_history.csv'):
    """Plot the historical portfolio value from the CSV file."""
    try:
        # Read the CSV file without headers, assign column names, and parse timestamp as index
        data = pd.read_csv(filename, header=None, names=['timestamp', 'total_value'], parse_dates=['timestamp'], index_col='timestamp')
        data.sort_index(inplace=True)

        # Plot the portfolio value
        plt.figure(figsize=(10, 6))
        plt.plot(data.index, data['total_value'], marker='o', linestyle='-', color='b')
        plt.title('Portfolio Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except FileNotFoundError:
        print(f"File {filename} not found. No data to plot.")
    except KeyError as e:
        print(f"KeyError: {e}. Check the column names in {filename}.")

# Example usage
plot_portfolio_history()
