from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.validators")

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """Symbol must be non-empty uppercase string."""
    if not symbol or not symbol.strip():
        raise ValueError("Symbol cannot be empty.")
    cleaned = symbol.strip().upper()
    logger.debug(f"Symbol validated: {cleaned}")
    return cleaned


def validate_side(side: str) -> str:
    """Side must be BUY or SELL."""
    cleaned = side.strip().upper()
    if cleaned not in VALID_SIDES:
        raise ValueError(f"Invalid side '{cleaned}'. Must be one of: {VALID_SIDES}")
    logger.debug(f"Side validated: {cleaned}")
    return cleaned


def validate_order_type(order_type: str) -> str:
    """Order type must be one of the supported types."""
    cleaned = order_type.strip().upper()
    if cleaned not in VALID_ORDER_TYPES:
        raise ValueError(f"Invalid order type '{cleaned}'. Must be one of: {VALID_ORDER_TYPES}")
    logger.debug(f"Order type validated: {cleaned}")
    return cleaned


def validate_quantity(quantity: str) -> float:
    """Quantity must be a positive number."""
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Quantity must be a number. Got: '{quantity}'")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero. Got: {qty}")
    logger.debug(f"Quantity validated: {qty}")
    return qty


def validate_price(price: str, order_type: str) -> float | None:
    """
    Price is required for LIMIT and STOP_MARKET orders.
    For MARKET orders, it's ignored.
    """
    if order_type == "MARKET":
        if price is not None:
            logger.debug("Price provided for MARKET order — will be ignored.")
        return None

    if price is None or str(price).strip() == "":
        raise ValueError(f"Price is required for {order_type} orders.")

    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Price must be a number. Got: '{price}'")

    if p <= 0:
        raise ValueError(f"Price must be greater than zero. Got: {p}")

    logger.debug(f"Price validated: {p}")
    return p


def validate_stop_price(stop_price: str, order_type: str) -> float | None:
    """Stop price is required only for STOP_MARKET orders."""
    if order_type != "STOP_MARKET":
        return None

    if stop_price is None or str(stop_price).strip() == "":
        raise ValueError("Stop price is required for STOP_MARKET orders.")

    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValueError(f"Stop price must be a number. Got: '{stop_price}'")

    if sp <= 0:
        raise ValueError(f"Stop price must be greater than zero. Got: {sp}")

    logger.debug(f"Stop price validated: {sp}")
    return sp


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str = None,
    stop_price: str = None
) -> dict:
    """
    Runs all validators in one go and returns a clean dict.
    This is what the CLI and order layer both call.
    """
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type.strip().upper()),
        "stop_price": validate_stop_price(stop_price, order_type.strip().upper()),
    }