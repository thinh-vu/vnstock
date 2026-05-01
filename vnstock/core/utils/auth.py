# vnstock/core/utils/auth.py

"""
User authentication and API key registration for vnstock.

Simple interface for users to register their API key.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def register_user(api_key: Optional[str] = None) -> bool:
    """
    Đăng ký người dùng với tham số API key tùy chọn.
    User registration with optional API key parameter.

    Hướng dẫn người dùng qua quá trình đăng ký để thiết lập API key của họ.
    Guides user through the registration process to set up their API key.

    Nếu api_key được cung cấp, sử dụng trực tiếp. Nếu không, hiển thị lời nhắc tương tác.
    If api_key is provided, uses it directly. Otherwise, shows interactive prompt.

    Args:
        api_key: Optional API key to register directly

    Returns:
        bool: True if registration successful, False otherwise
    """
    try:
        # Check vnai availability
        import vnai

        _ = vnai  # Use the import to avoid unused warning
    except ImportError:
        print("✗ Lỗi: vnai module không được tìm thấy (✗ Error: vnai module not found)")
        return False

    # If API key is provided as parameter, use it directly
    if api_key:
        return _register_api_key_directly(api_key)

    # Otherwise, show interactive registration
    return _register_interactive()


def _register_api_key_directly(api_key: str) -> bool:
    """
    Đăng ký API key trực tiếp mà không cần lời nhắc tương tác.
    Register API key directly without interactive prompts.

    Args:
        api_key: API key to register

    Returns:
        bool: True if successful, False otherwise
    """
    if not api_key or len(api_key) < 10:
        print("✗ API key không hợp lệ")
        return False

    try:
        from vnai import setup_api_key

        if setup_api_key(api_key):
            # Show masked API key after successful registration
            if len(api_key) > 8:
                masked_key = f"{api_key[:4]}***{api_key[-4:]}"
            else:
                masked_key = api_key[:8] + "***" if len(api_key) > 4 else "****"

            print(
                f"✓ API key đã được lưu thành công! (✓ API key saved successfully! {masked_key}"
            )
            print(
                "✓ Bạn đang sử dụng gói Cộng đồng (✓ You are using Community Edition - 60 requests/min)"
            )
            return True
    except Exception as e:
        logger.debug(f"Direct setup failed: {e}")
        print("✗ Không thể lưu API key")

    return False


def _register_interactive() -> bool:
    """
    Interactive registration with user prompts.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from vnai import check_api_key_status, setup_api_key
    except ImportError:
        print("✗ Lỗi: vnai module không được tìm thấy (✗ Error: vnai module not found)")
        return False

    print("\n" + "=" * 70)
    print("  VNSTOCK - ĐĂNG KÝ API KEY")
    print("=" * 70)

    # Check if already registered
    try:
        status = check_api_key_status()
        if status.get("has_api_key"):
            # Show masked API key (first 4, last 4, with *** in middle)
            api_key = status.get("api_key_preview", "")
            if len(api_key) > 8:
                masked_key = f"{api_key[:4]}***{api_key[-4:]}"
            else:
                masked_key = api_key[:8] + "***" if len(api_key) > 4 else "****"

            print(f"\n✓ API key: {masked_key}")
            print(f"✓ Tier (Gói): {status.get('tier', 'unknown')}")
            print(f"✓ Giới hạn (Limits): {status.get('limits', {})}")

            change = (
                input(
                    "\nBạn muốn thay đổi API key? (Do you want to change API key?) [y/N]: "
                )
                .strip()
                .lower()
            )
            if change != "y":
                return True
    except Exception:
        pass

    print("""
🚀 Đăng ký API key để tăng giới hạn sử dụng (🚀 Register API key to increase rate limits):

  • Khách (Guest): 20 requests/phút - không cần đăng ký (20 requests/min - no registration needed)
  • Cộng đồng (Community): 60 requests/phút - đăng ký miễn phí (60 requests/min - free registration)
  • Tài trợ (Sponsor): 180-600 requests/phút (180-600 requests/min)

📌 Đăng nhập Google để tạo tài khoản và lấy API key miễn phí tại: https://vnstocks.com/login (Login with Google to create an account and get a free API key at: https://vnstocks.com/login)
""")

    # Get API key from user directly (no Enter step)
    max_attempts = 3
    for attempt in range(max_attempts):
        api_key = input("\nNhập API key của bạn: ").strip()

        if not api_key:
            print("✗ API key không được để trống (✗ API key cannot be empty)")
            if attempt < max_attempts - 1:
                print(f"  Vui lòng thử lại ({max_attempts - attempt - 1} lần còn lại)")
            continue

        if len(api_key) < 10:
            print("✗ API key quá ngắn")
            if attempt < max_attempts - 1:
                print(f"  Vui lòng thử lại ({max_attempts - attempt - 1} lần còn lại)")
            continue

        # Try to save API key
        try:
            if setup_api_key(api_key):
                # Show masked API key after successful registration
                if len(api_key) > 8:
                    masked_key = f"{api_key[:4]}***{api_key[-4:]}"
                else:
                    masked_key = api_key[:8] + "***" if len(api_key) > 4 else "****"

                print(
                    f"\n✓ API key đã được lưu thành công! (✓ API key saved successfully!) {masked_key}"
                )
                print(
                    "✓ Bạn đang sử dụng gói Cộng đồng (✓ You are using Community Edition - 60 requests/min)"
                )
                print("\n🎉 Đăng ký thành công! (🎉 Registration successful!)")
                return True
        except Exception as e:
            logger.debug(f"Setup failed: {e}")
            print("✗ Không thể lưu API key")
            if attempt < max_attempts - 1:
                print(f"  Vui lòng thử lại ({max_attempts - attempt - 1} lần còn lại)")

    print("\n✗ Đăng ký thất bại")
    return False


def change_api_key(api_key: str) -> bool:
    """
    Change API key directly.

    Args:
        api_key: New API key

    Returns:
        bool: True if successful, False otherwise
    """
    if not api_key or len(api_key) < 10:
        print("✗ API key không hợp lệ")
        return False

    try:
        from vnai import setup_api_key

        if setup_api_key(api_key):
            print("✓ API key đã được cập nhật (✓ API key updated)")
            return True
    except Exception as e:
        logger.debug(f"Change failed: {e}")
        print("✗ Không thể cập nhật API key")

    return False


def check_status() -> Optional[dict]:
    """
    Check current registration status.

    Returns:
        dict: Status information or None if error
    """
    try:
        from vnai import check_api_key_status

        status = check_api_key_status()

        if status.get("has_api_key"):
            print(f"✓ API key: {status.get('api_key_preview')}")
            print(f"  Tier: {status.get('tier')}")
            print(
                f"  Giới hạn: {status.get('limits', {}).get('per_minute')} requests/phút"
            )
        else:
            print("✗ Chưa đăng ký API key (✗ API key not registered)")
            print("  Tier: Guest (20 requests/phút)")

        return status
    except Exception as e:
        logger.debug(f"Status check failed: {e}")
        print("✗ Không thể kiểm tra trạng thái")
        return None
