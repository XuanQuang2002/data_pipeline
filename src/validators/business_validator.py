import re
import pandas as pd

EMAIL = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

VALID = {
    "customers": {
        "status": {
            "active",
            "inactive",
        }
    },

    "products": {
        "status": {
            "active",
            "inactive",
            "discontinued",
        }
    },

    "orders": {
        "status": {
            "pending",
            "confirmed",
            "shipped",
            "completed",
            "cancelled",
        },
        "channel": {
            "web",
            "mobile_app",
            "social",
        },
    },

    "payments": {
        "payment_status": {
            "pending",
            "success",
            "failed",
            "refunded",
        },
        "payment_method": {
            "cash",
            "bank_transfer",
            "card",
            "e_wallet",
        },
    },
}

def split_valid_invalid(name, df):
    """TODO Buổi 7: row-level rules.

    Gợi ý: email, enum status/channel/method, non-negative money,
    quantity > 0, discount <= quantity*unit_price, parseable required dates.
    Return: (valid_df, reject_df có error_code).
    """
    errs = []

    for idx, row in df.iterrows():
        e = []
        # Domain / enum
        for col, allowed in VALID.get(name,{}).items():
            if (col in df and row[col] not in allowed):
                e.append(f"INVALID_{col.upper()}")
        # Email
        if name == "customers":
            if (
                not isinstance(row.get("email"),str)
                or not EMAIL.match(row["email"])
            ):
                e.append(
                    "INVALID_EMAIL"
                )
        # Product price
        if name == "products":
            if (
                pd.to_numeric(row.get("unit_price"),errors="coerce") < 0
            ):
                e.append("NEGATIVE_PRICE")
        # Order item
        if name == "order_items":
            if (
                pd.to_numeric(row.get("quantity"),errors="coerce") <= 0
            ):
                e.append("INVALID_QUANTITY")

            if (
                pd.to_numeric(row.get("discount_amount"),errors="coerce") < 0
            ):
                e.append("NEGATIVE_DISCOUNT")

            if (
                pd.to_numeric(row.get("unit_price"),errors="coerce") < 0 
            ):
                e.append("NEGATIVE_PRICE")

            gross = (pd.to_numeric(row.get("quantity"),errors="coerce") 
                     * pd.to_numeric(row.get("unit_price"),errors="coerce"))
            if (
                pd.to_numeric(row.get("discount_amount"),errors="coerce")
                > gross
            ):
                e.append("DISCOUNT_EXCEEDS_GROSS")
        # Payment
        if name == "payments":
            if (
                pd.to_numeric(row.get("amount"),errors="coerce") < 0
            ):
                e.append("NEGATIVE_AMOUNT")
        # Required IDs / full_name
        required_candidates = [
            "customer_id",
            "product_id",
            "order_id",
            "order_item_id",
            "payment_id",
            "full_name",
        ]
        if any(
            (pd.isna(row.get(c))or row.get(c) == "")
            for c in df.columns
            if c in required_candidates
        ):
            e.append("MISSING_REQUIRED")

        errs.append("|".join(e))
    out = df.copy()
    out["error_code"] = errs

    valid = (
        out[out.error_code == ""].drop(
            columns="error_code"
        )
    )

    reject = out[out.error_code != ""]
    return valid, reject
