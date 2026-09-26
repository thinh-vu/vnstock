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
    Save the user's API key so vnstock can use it in later sessions.

    Run it with no argument: the key is typed at a hidden prompt, so it never lands
    in shell history, a notebook cell or an AI assistant's conversation log. If the
    `VNSTOCK_API_KEY` environment variable is set, it offers to save that instead.

    Passing `api_key` still works for backward compatibility, but it puts the key
    in your code or command line; prefer the prompt or the environment variable.

    Args:
        api_key: Optional API key to register directly

    Returns:
        bool: True if registration successful, False otherwise
    """
    try:
        import vnai  # noqa: F401
    except ImportError:
        print("✗ Lỗi: vnai module không được tìm thấy (✗ Error: vnai module not found)")
        return False

    if api_key:
        return _register_api_key_directly(api_key)

    return _register_interactive()


def _mask(api_key: str) -> str:
    """First and last 4 characters only; short keys are hidden entirely."""
    return f"{api_key[:4]}***{api_key[-4:]}" if len(api_key) > 12 else "***"


def _register_api_key_directly(api_key: str) -> bool:
    """
    Register an API key without the interactive prompt.

    `vnai.setup_api_key` prints its own confirmation, so nothing is printed here on
    success. Earlier versions also printed "you are using the Community edition",
    which was wrong for sponsors and sent them to support asking why.

    Args:
        api_key: API key to register

    Returns:
        bool: True if successful, False otherwise
    """
    api_key = (api_key or "").strip()
    if len(api_key) < 10:
        print("✗ API key không hợp lệ (✗ Invalid API key)")
        return False

    try:
        from vnai import setup_api_key

        if setup_api_key(api_key):
            return True
    except Exception as e:
        logger.debug(f"Direct setup failed: {e}")
    print("✗ Không thể lưu API key (✗ Could not save the API key)")
    return False


def _read_key_hidden(prompt: str) -> str:
    """
    Read a secret without echoing it.

    `input()` showed the key on screen and, in Jupyter, left it in the cell output
    saved with the notebook. `getpass` hides it in terminals and renders a password
    box in Jupyter.
    """
    import getpass

    try:
        return getpass.getpass(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def _register_interactive() -> bool:
    """
    Interactive registration with user prompts.

    Returns:
        bool: True if successful, False otherwise
    """
    import os

    try:
        from vnai import check_api_key_status, setup_api_key
    except ImportError:
        print("✗ Lỗi: vnai module không được tìm thấy (✗ Error: vnai module not found)")
        return False

    print("\n" + "=" * 70)
    print("  VNSTOCK - ĐĂNG KÝ API KEY")
    print("=" * 70)

    # check_api_key_status() prints the masked key, tier and limits itself.
    try:
        status = check_api_key_status()
        if status.get("has_api_key"):
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

    env_key = (os.environ.get("VNSTOCK_API_KEY") or "").strip()
    if len(env_key) >= 10:
        answer = (
            input(
                f"\nĐã có khoá trong biến VNSTOCK_API_KEY ({_mask(env_key)}). "
                "Lưu khoá này? (Save this key?) [Y/n]: "
            )
            .strip()
            .lower()
        )
        if answer in ("", "y", "yes", "c", "co", "có"):
            return _register_api_key_directly(env_key)

    print("""
🚀 Đăng ký API key để tăng giới hạn sử dụng (🚀 Register API key to increase rate limits):

  • Khách (Guest): 20 requests/phút - không cần đăng ký (20 requests/min - no registration needed)
  • Cộng đồng (Community): 60 requests/phút - đăng ký miễn phí (60 requests/min - free registration)
  • Tài trợ (Sponsor): 180-600 requests/phút (180-600 requests/min)

📌 Lấy API key tại (Get your API key at): https://vnstocks.com/account#api-key
   Khoá được nhập ẩn, không hiện trên màn hình (The key is not shown as you type or paste).
""")

    max_attempts = 3
    for attempt in range(max_attempts):
        api_key = _read_key_hidden("Dán API key rồi nhấn Enter (Paste your API key, then Enter): ")

        if not api_key:
            print("✗ API key không được để trống (✗ API key cannot be empty)")
        elif len(api_key) < 10:
            print("✗ API key quá ngắn (✗ API key is too short)")
        else:
            try:
                if setup_api_key(api_key):
                    print(f"\n🎉 Đăng ký thành công! (🎉 Registration successful!) {_mask(api_key)}")
                    return True
            except Exception as e:
                logger.debug(f"Setup failed: {e}")
            print("✗ Không thể lưu API key (✗ Could not save the API key)")

        if attempt < max_attempts - 1:
            print(f"  Vui lòng thử lại ({max_attempts - attempt - 1} lần còn lại)")

    print("\n✗ Đăng ký thất bại (✗ Registration failed)")
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

        # vnai already printed the masked key, tier and limits when a key exists.
        if not status.get("has_api_key"):
            print("✗ Chưa đăng ký API key (✗ API key not registered)")
            print("  Tier: Guest (20 requests/phút)")

        return status
    except Exception as e:
        logger.debug(f"Status check failed: {e}")
        print("✗ Không thể kiểm tra trạng thái")
        return None
