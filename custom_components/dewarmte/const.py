DOMAIN = "dewarmte"
PLATFORMS = ["sensor", "binary_sensor"]

API_BASE_URL = "https://api.mydewarmte.com"
API_TOKEN_URL = f"{API_BASE_URL}/v1/auth/token/"
TOKEN_REFRESH_MIN = 30
API_REFRESH_URL = f"{API_BASE_URL}/v1/auth/token/refresh/"
API_PRODUCTS_PATH = f"/v1/customer/products/"