import pandas as pd
from fastapi import HTTPException

class PlatformHandler:

    @staticmethod
    def sanitize(df: pd.DataFrame, platform: str) -> pd.DataFrame:
        platform = platform.lower()

        if platform == "shopify":
            return PlatformHandler._sanitize_shopify(df)
        elif platform == "magento":
            return PlatformHandler._sanitize_magento(df)
        elif platform == "woocommerce":
            return PlatformHandler._sanitize_woocommerce(df)
        elif platform == "bigcommerce":
            return PlatformHandler._sanitize_bigcommerce(df)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    @staticmethod
    def _sanitize_shopify(df: pd.DataFrame) -> pd.DataFrame:
        # Shopify export structure mapping → our standardized fields
        mapping = {
            "Handle": "product_id",
            "Title": "name",
            "Body (HTML)": "description",
            "Variant Price": "price"
        }

        sanitized_df = df.rename(columns=mapping)

        # Keep only necessary columns
        sanitized_df = sanitized_df[["product_id", "name", "description", "price"]]

        return PlatformHandler._validate_and_filter(sanitized_df)

    @staticmethod
    def _sanitize_magento(df: pd.DataFrame) -> pd.DataFrame:
        mapping = {
            "entity_id": "product_id",
            "name": "name",
            "description": "description",
            "price": "price"
        }

        sanitized_df = df.rename(columns=mapping)
        return PlatformHandler._validate_and_filter(sanitized_df)

    @staticmethod
    def _sanitize_woocommerce(df: pd.DataFrame) -> pd.DataFrame:
        mapping = {
            "id": "product_id",
            "name": "name",
            "short_description": "description",
            "price": "price"
        }

        sanitized_df = df.rename(columns=mapping)
        return PlatformHandler._validate_and_filter(sanitized_df)

    @staticmethod
    def _sanitize_bigcommerce(df: pd.DataFrame) -> pd.DataFrame:
        mapping = {
            "id": "product_id",
            "name": "name",
            "description": "description",
            "price": "price"
        }

        sanitized_df = df.rename(columns=mapping)
        return PlatformHandler._validate_and_filter(sanitized_df)

    @staticmethod
    def _validate_and_filter(df: pd.DataFrame) -> pd.DataFrame:
        required_columns = ["product_id", "name", "description", "price"]

        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

        # Drop rows with null required fields and invalid prices
        df = df.dropna(subset=required_columns)
        df = df[df["price"].apply(lambda x: isinstance(x, (int, float)) and x > 0)]

        return df

