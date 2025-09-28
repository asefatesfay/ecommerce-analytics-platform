"""
Data Generation Utilities for E-commerce Analytics
=================================================

This module provides utilities to generate realistic e-commerce data
including customers, products, orders, and web analytics data.
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple

# Set seeds for reproducible data
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)


class EcommerceDataGenerator:
    """Generate realistic e-commerce datasets."""

    def __init__(
        self,
        num_customers: int = 10000,
        num_products: int = 1000,
        num_orders: int = 50000,
        start_date: str = "2022-01-01",
        end_date: str = "2024-12-31",
    ):

        self.num_customers = num_customers
        self.num_products = num_products
        self.num_orders = num_orders
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

        # Business parameters for realism
        self.customer_segments = ["Budget", "Standard", "Premium", "Enterprise"]
        self.acquisition_channels = [
            "Organic Search",
            "Paid Search",
            "Social Media",
            "Email Marketing",
            "Direct",
            "Referral",
            "Affiliate",
        ]
        self.product_categories = [
            "Electronics",
            "Clothing",
            "Home & Garden",
            "Books",
            "Sports",
            "Health & Beauty",
            "Toys",
            "Automotive",
        ]

    def generate_customers(self) -> pd.DataFrame:
        """Generate customer data with demographics and acquisition info."""
        print(f"🏃‍♂️ Generating {self.num_customers:,} customers...")

        customers = []
        for i in range(self.num_customers):
            # Demographics
            profile = fake.profile()

            # Customer segment (affects spending behavior)
            segment = np.random.choice(self.customer_segments, p=[0.3, 0.4, 0.25, 0.05])  # Realistic distribution

            # Acquisition channel
            channel = np.random.choice(self.acquisition_channels, p=[0.25, 0.2, 0.15, 0.15, 0.1, 0.08, 0.07])

            # Registration date (weighted towards recent)
            days_back = np.random.exponential(200)  # Exponential decay
            days_back = min(days_back, (self.end_date - self.start_date).days)
            registration_date = self.end_date - timedelta(days=int(days_back))

            customer = {
                "customer_id": i + 1,
                "email": profile["mail"],
                "first_name": profile["name"].split()[0],
                "last_name": profile["name"].split()[-1],
                "birth_date": profile["birthdate"],
                "gender": profile["sex"],
                "address": profile["address"],
                "city": fake.city(),
                "country": fake.country(),
                "postal_code": fake.postcode(),
                "customer_segment": segment,
                "acquisition_channel": channel,
                "registration_date": registration_date,
                "is_active": np.random.choice([True, False], p=[0.85, 0.15]),
            }
            customers.append(customer)

        df = pd.DataFrame(customers)
        print(f"✅ Generated customers with segments: {df['customer_segment'].value_counts().to_dict()}")
        return df

    def generate_products(self) -> pd.DataFrame:
        """Generate product catalog with categories, pricing, and inventory."""
        print(f"📦 Generating {self.num_products:,} products...")

        products = []
        for i in range(self.num_products):
            category = np.random.choice(self.product_categories)

            # Price based on category (some categories are more expensive)
            category_price_multipliers = {
                "Electronics": 3.0,
                "Automotive": 2.5,
                "Home & Garden": 1.8,
                "Health & Beauty": 1.2,
                "Clothing": 1.0,
                "Sports": 1.5,
                "Books": 0.4,
                "Toys": 0.8,
            }

            base_price = np.random.lognormal(3, 1)  # Log-normal for realistic price distribution
            price = base_price * category_price_multipliers.get(category, 1.0)

            # Cost (margin varies by category)
            margin_rate = np.random.normal(0.4, 0.1)  # Average 40% margin
            margin_rate = max(0.1, min(0.8, margin_rate))  # Constrain between 10-80%
            cost = price * (1 - margin_rate)

            product = {
                "product_id": i + 1,
                "product_name": f"{fake.word().title()} {fake.word().title()}",
                "category": category,
                "subcategory": f"{category} - {fake.word().title()}",
                "brand": fake.company(),
                "price": round(price, 2),
                "cost": round(cost, 2),
                "weight_kg": round(np.random.lognormal(0, 1), 2),
                "dimensions_cm": f"{fake.random_int(5,50)}x{fake.random_int(5,50)}x{fake.random_int(2,20)}",
                "launch_date": fake.date_between(start_date=self.start_date.date(), end_date=self.end_date.date()),
                "is_active": np.random.choice([True, False], p=[0.9, 0.1]),
            }
            products.append(product)

        df = pd.DataFrame(products)
        print(f"✅ Generated products across categories: {df['category'].value_counts().to_dict()}")
        return df

    def generate_orders(
        self, customers_df: pd.DataFrame, products_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate orders and order items with realistic patterns."""
        print(f"🛒 Generating {self.num_orders:,} orders with realistic patterns...")

        orders = []
        order_items = []

        # Customer behavior patterns by segment
        segment_behavior = {
            "Budget": {
                "avg_order_value": 50,
                "order_frequency": 0.3,
                "items_per_order": 2,
            },
            "Standard": {
                "avg_order_value": 120,
                "order_frequency": 0.5,
                "items_per_order": 3,
            },
            "Premium": {
                "avg_order_value": 300,
                "order_frequency": 0.7,
                "items_per_order": 5,
            },
            "Enterprise": {
                "avg_order_value": 800,
                "order_frequency": 0.9,
                "items_per_order": 10,
            },
        }

        for order_id in range(1, self.num_orders + 1):
            # Select customer (weighted by segment activity)
            segment_weights = (
                customers_df["customer_segment"].map(lambda x: segment_behavior[x]["order_frequency"]).values
            )
            customer = customers_df.sample(1, weights=segment_weights).iloc[0]

            # Order date (more recent orders more likely, seasonal patterns)
            days_range = (self.end_date - self.start_date).days

            # Add seasonality (higher sales in Nov-Dec, lower in Jan-Feb)
            month_weights = [0.7, 0.7, 0.9, 0.9, 1.0, 1.0, 0.8, 0.8, 1.1, 1.1, 1.4, 1.5]

            # Random date with recent bias
            days_back = np.random.exponential(30)  # More recent orders more likely
            days_back = min(days_back, days_range)
            order_date = self.end_date - timedelta(days=int(days_back))

            # Adjust for seasonality
            month_weight = month_weights[order_date.month - 1]
            if np.random.random() > month_weight / 1.5:  # Skip some orders based on seasonality
                continue

            # Order status (most orders completed)
            status = np.random.choice(
                ["Completed", "Pending", "Cancelled", "Returned"],
                p=[0.85, 0.05, 0.05, 0.05],
            )

            # Shipping and payment info
            shipping_cost = np.random.normal(10, 3) if np.random.random() > 0.1 else 0  # 10% free shipping
            shipping_cost = max(0, shipping_cost)

            payment_method = np.random.choice(
                ["Credit Card", "Debit Card", "PayPal", "Bank Transfer"],
                p=[0.6, 0.25, 0.1, 0.05],
            )

            order = {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": order_date,
                "status": status,
                "payment_method": payment_method,
                "shipping_cost": round(shipping_cost, 2),
                "discount_amount": 0,  # Will calculate after items
                "tax_amount": 0,  # Will calculate after items
                "total_amount": 0,  # Will calculate after items
            }

            # Generate order items
            segment = customer["customer_segment"]
            behavior = segment_behavior[segment]

            # Number of items (Poisson distribution around segment average)
            num_items = max(1, np.random.poisson(behavior["items_per_order"]))

            order_total = 0
            selected_products = products_df.sample(min(num_items, len(products_df)))

            for _, product in selected_products.iterrows():
                quantity = max(1, np.random.poisson(2))  # Most orders have 1-3 of each item

                # Price variations (promotions, dynamic pricing)
                price_variation = np.random.normal(1.0, 0.1)  # ±10% price variation
                unit_price = product["price"] * max(0.5, price_variation)  # Min 50% of base price

                item_total = quantity * unit_price
                order_total += item_total

                order_item = {
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": round(unit_price, 2),
                    "total_price": round(item_total, 2),
                }
                order_items.append(order_item)

            # Calculate order totals
            discount_rate = 0
            if order_total > 200:  # Discounts for larger orders
                discount_rate = np.random.uniform(0.05, 0.15)
            elif np.random.random() < 0.1:  # Random promotional discounts
                discount_rate = np.random.uniform(0.1, 0.25)

            discount_amount = order_total * discount_rate
            subtotal = order_total - discount_amount
            tax_rate = 0.08  # 8% tax rate
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount + shipping_cost

            # Update order totals
            order.update(
                {
                    "discount_amount": round(discount_amount, 2),
                    "tax_amount": round(tax_amount, 2),
                    "total_amount": round(total_amount, 2),
                }
            )

            orders.append(order)

        orders_df = pd.DataFrame(orders)
        order_items_df = pd.DataFrame(order_items)

        print(f"✅ Generated {len(orders_df):,} orders and {len(order_items_df):,} order items")
        print(f"   Order statuses: {orders_df['status'].value_counts().to_dict()}")
        print(f"   Avg order value: ${orders_df['total_amount'].mean():.2f}")

        return orders_df, order_items_df

    def generate_web_analytics(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Generate web analytics data (sessions, page views, conversions)."""
        print("🌐 Generating web analytics data...")

        sessions = []

        # Generate more sessions than orders (not every session converts)
        num_sessions = len(orders_df) * 5  # 20% conversion rate

        for session_id in range(1, num_sessions + 1):
            # Random or existing customer
            if np.random.random() < 0.6:  # 60% are existing customers
                customer_id = customers_df.sample(1)["customer_id"].iloc[0]
            else:
                customer_id = None  # Anonymous session

            # Session timing (similar to order patterns)
            days_back = np.random.exponential(20)
            session_date = self.end_date - timedelta(days=int(days_back))

            # Traffic sources
            traffic_source = np.random.choice(
                [
                    "organic_search",
                    "paid_search",
                    "social",
                    "email",
                    "direct",
                    "referral",
                ],
                p=[0.35, 0.25, 0.15, 0.1, 0.1, 0.05],
            )

            # Device type
            device_type = np.random.choice(["desktop", "mobile", "tablet"], p=[0.4, 0.5, 0.1])

            # Session metrics
            session_duration = max(30, np.random.exponential(300))  # Seconds
            page_views = max(1, np.random.poisson(3))
            bounce_rate = 1 if page_views == 1 else 0

            # Conversion (did this session result in an order?)
            converted = session_id <= len(orders_df)  # First N sessions converted

            session = {
                "session_id": session_id,
                "customer_id": customer_id,
                "session_date": session_date,
                "traffic_source": traffic_source,
                "device_type": device_type,
                "session_duration_seconds": int(session_duration),
                "page_views": page_views,
                "bounced": bounce_rate,
                "converted": converted,
                "revenue": (orders_df.iloc[session_id - 1]["total_amount"] if converted else 0),
            }
            sessions.append(session)

        sessions_df = pd.DataFrame(sessions)
        print(f"✅ Generated {len(sessions_df):,} web sessions")
        print(f"   Conversion rate: {sessions_df['converted'].mean()*100:.1f}%")
        print(f"   Traffic sources: {sessions_df['traffic_source'].value_counts().to_dict()}")

        return sessions_df

    def generate_all_data(self) -> Dict[str, pd.DataFrame]:
        """Generate all datasets and return as dictionary."""
        print("🚀 Starting comprehensive e-commerce data generation...")
        print(
            f"Parameters: {self.num_customers:,} customers, {self.num_products:,} products, {self.num_orders:,} orders"
        )
        print(f"Date range: {self.start_date.date()} to {self.end_date.date()}")
        print("-" * 60)

        # Generate in order (dependencies)
        customers_df = self.generate_customers()
        products_df = self.generate_products()
        orders_df, order_items_df = self.generate_orders(customers_df, products_df)
        sessions_df = self.generate_web_analytics(customers_df, orders_df)

        print("-" * 60)
        print("🎉 Data generation completed successfully!")

        return {
            "customers": customers_df,
            "products": products_df,
            "orders": orders_df,
            "order_items": order_items_df,
            "web_sessions": sessions_df,
        }
