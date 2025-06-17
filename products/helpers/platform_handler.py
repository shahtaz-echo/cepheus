import pandas as pd
from fastapi import HTTPException

class PlatformHandler:

    @staticmethod
    def sanitize(df: pd.DataFrame, platform: str) -> pd.DataFrame:
        platform = platform.lower()

        if platform == "shopify":
            return PlatformHandler._sanitize_shopify(df)
        
        if platform == "shopify_json":
            return PlatformHandler._sanitize_shopify_json(df)
        
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
    def _sanitize_shopify_json(df: pd.DataFrame) -> pd.DataFrame:
        # Shopify export structure mapping → our standardized fields
        mapping = {
            "id": "product_id",
            "name": "name",
            "description": "description",
            "price": "price"
        }

        # Check if required columns exist
        missing_columns = []
        for original_col in mapping.keys():
            if original_col not in df.columns:
                missing_columns.append(original_col)
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns in data: {missing_columns}. Available columns: {list(df.columns)}"
            )

        # Rename columns
        sanitized_df = df.rename(columns=mapping)

        # Keep only necessary columns
        required_columns = ["product_id", "name", "description", "price"]
        sanitized_df = sanitized_df[required_columns]

        return PlatformHandler._validate_and_filter(sanitized_df)
    
    
    @staticmethod
    def _sanitize_magento(df: pd.DataFrame) -> pd.DataFrame:
        mapping = {
            "product_id": "product_id",
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
        """Validate and clean the sanitized data"""
        df = df.dropna(subset=['product_id'])
        df = df[df['product_id'].astype(str).str.strip() != '']
        
        # Fill NaN values
        df['name'] = df['name'].fillna('')
        df['description'] = df['description'].fillna('')
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
        
        # Convert product_id to string
        df['product_id'] = df['product_id'].astype(str)
        
        return df

